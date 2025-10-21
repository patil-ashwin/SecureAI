"""
PII Detection Engine.

Detects personally identifiable information (PII) in text using regex patterns
and optional NER (Named Entity Recognition).
"""

import re
from typing import Optional, List, Set
from collections import defaultdict

from secureai.detection.entities import EntityType, PIIEntity, DetectionResult
from secureai.detection.patterns import PIIPatterns
from secureai.core.exceptions import DetectionError


class PIIDetector:
    """
    PII Detection Engine using regex patterns and optional NER.
    
    This detector finds various types of sensitive information in text including:
    - Social Security Numbers
    - Credit Card Numbers
    - Email Addresses
    - Phone Numbers
    - IP Addresses
    - API Keys
    - And many more...
    
    Examples:
        >>> detector = PIIDetector()
        >>> result = detector.detect("John's SSN is 123-45-6789 and email is john@example.com")
        >>> len(result.entities)
        2
        >>> result.entities[0].entity_type
        'SSN'
    """

    def __init__(
        self,
        enabled_types: Optional[Set[EntityType]] = None,
        min_confidence: float = 0.5,
        use_context: bool = True,
    ):
        """
        Initialize PII detector.
        
        Args:
            enabled_types: Set of entity types to detect. If None, detect all types.
            min_confidence: Minimum confidence score to include entity (0-1)
            use_context: Whether to extract surrounding context for entities
        """
        self.enabled_types = enabled_types or set(EntityType)
        self.min_confidence = min_confidence
        self.use_context = use_context
        self.patterns = PIIPatterns.get_all_patterns()
        
        # Filter patterns to only enabled types
        self.active_patterns = {
            etype: pattern
            for etype, pattern in self.patterns.items()
            if etype in self.enabled_types
        }

    def detect(self, text: str) -> DetectionResult:
        """
        Detect PII entities in text.
        
        Args:
            text: Text to scan for PII
        
        Returns:
            DetectionResult with all detected entities
            
        Raises:
            DetectionError: If detection fails
        """
        if not text:
            return DetectionResult(text=text, entities=[])

        try:
            entities: List[PIIEntity] = []
            
            # Run regex-based detection
            entities.extend(self._detect_with_regex(text))
            
            # Remove duplicates and overlaps
            entities = self._remove_duplicates(entities)
            
            # Sort by position
            entities.sort(key=lambda e: e.start)
            
            return DetectionResult(text=text, entities=entities)
            
        except Exception as e:
            raise DetectionError(f"PII detection failed: {str(e)}") from e

    def _detect_with_regex(self, text: str) -> List[PIIEntity]:
        """
        Detect PII using regex patterns.
        
        Args:
            text: Text to scan
        
        Returns:
            List of detected entities
        """
        entities = []
        
        for entity_type, pattern in self.active_patterns.items():
            for match in pattern.finditer(text):
                # Extract matched value
                value = match.group(0)
                start = match.start()
                end = match.end()
                
                # Calculate confidence based on pattern specificity
                confidence = self._calculate_confidence(entity_type, value, text, start, end)
                
                if confidence < self.min_confidence:
                    continue
                
                # Extract context if enabled
                context = None
                if self.use_context:
                    context = self._extract_context(text, start, end)
                
                entity = PIIEntity(
                    entity_type=entity_type,
                    value=value,
                    start=start,
                    end=end,
                    confidence=confidence,
                    context=context,
                )
                
                entities.append(entity)
        
        # Special case: Additional PERSON detection with simpler pattern
        if EntityType.PERSON in self.enabled_types:
            simple_person_pattern = PIIPatterns.PERSON_SIMPLE
            for match in simple_person_pattern.finditer(text):
                value = match.group(0)
                start = match.start()
                end = match.end()
                
                # Check if this person name is already detected
                already_detected = any(
                    entity.entity_type == EntityType.PERSON and 
                    entity.value == value and 
                    entity.start == start
                    for entity in entities
                )
                
                if not already_detected:
                    # Calculate confidence for simple person pattern
                    confidence = self._calculate_confidence(EntityType.PERSON, value, text, start, end)
                    
                    if confidence >= self.min_confidence:
                        context = None
                        if self.use_context:
                            context = self._extract_context(text, start, end)
                        
                        entity = PIIEntity(
                            entity_type=EntityType.PERSON,
                            value=value,
                            start=start,
                            end=end,
                            confidence=confidence,
                            context=context
                        )
                        entities.append(entity)
        
        return entities

    def _calculate_confidence(
        self, entity_type: EntityType, value: str, text: str, start: int, end: int
    ) -> float:
        """
        Calculate confidence score for detected entity.
        
        Higher confidence for:
        - More specific patterns
        - Proper context (e.g., "SSN:" before a number)
        - Valid checksums (for credit cards)
        
        Args:
            entity_type: Type of entity
            value: Detected value
            text: Full text
            start: Start position
            end: End position
        
        Returns:
            Confidence score (0-1)
        """
        base_confidence = 0.8  # Base confidence for regex match
        
        # Check for contextual keywords before the match
        context_before = text[max(0, start - 20):start].lower()
        
        confidence_boosts = {
            EntityType.SSN: ["ssn", "social security", "social-security"],
            EntityType.CREDIT_CARD: ["card", "credit", "cc", "payment"],
            EntityType.EMAIL: ["email", "e-mail", "contact"],
            EntityType.PHONE: ["phone", "tel", "call", "mobile"],
            EntityType.API_KEY: ["api", "key", "token", "secret"],
            EntityType.PASSWORD: ["password", "passwd", "pwd", "pass"],
        }
        
        if entity_type in confidence_boosts:
            if any(keyword in context_before for keyword in confidence_boosts[entity_type]):
                base_confidence += 0.15
        
        # Special validation for certain types
        if entity_type == EntityType.CREDIT_CARD:
            if self._validate_luhn(value):
                base_confidence += 0.1
            else:
                base_confidence -= 0.3  # Likely false positive
        
        if entity_type == EntityType.SSN:
            # Additional SSN validation
            digits = re.sub(r'\D', '', value)
            if len(digits) == 9:
                # Check for invalid SSN patterns (000, 666, 900-999 in first 3 digits)
                first_three = int(digits[:3])
                if first_three == 0 or first_three == 666 or first_three >= 900:
                    base_confidence -= 0.5
        
        # Cap confidence at 1.0
        return min(base_confidence, 1.0)

    def _validate_luhn(self, card_number: str) -> bool:
        """
        Validate credit card number using Luhn algorithm.
        
        Args:
            card_number: Credit card number string
        
        Returns:
            True if valid, False otherwise
        """
        # Remove non-digits
        digits = [int(d) for d in re.sub(r'\D', '', card_number)]
        
        if len(digits) < 13 or len(digits) > 19:
            return False
        
        # Luhn algorithm
        checksum = 0
        reverse_digits = digits[::-1]
        
        for i, digit in enumerate(reverse_digits):
            if i % 2 == 1:  # Every second digit from the right
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        
        return checksum % 10 == 0

    def _extract_context(self, text: str, start: int, end: int, window: int = 30) -> str:
        """
        Extract surrounding context for an entity.
        
        Args:
            text: Full text
            start: Entity start position
            end: Entity end position
            window: Number of characters to include on each side
        
        Returns:
            Context string with entity placeholder
        """
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        
        before = text[context_start:start]
        after = text[end:context_end]
        
        return f"{before}[ENTITY]{after}"

    def _remove_duplicates(self, entities: List[PIIEntity]) -> List[PIIEntity]:
        """
        Remove duplicate and overlapping entities.
        
        When entities overlap, keep the one with higher confidence.
        
        Args:
            entities: List of detected entities
        
        Returns:
            Filtered list without duplicates
        """
        if not entities:
            return entities
        
        # Sort by start position, then by confidence (descending)
        sorted_entities = sorted(entities, key=lambda e: (e.start, -e.confidence))
        
        filtered = []
        for entity in sorted_entities:
            # Check if this entity overlaps with any already-filtered entity
            overlaps = False
            for existing in filtered:
                if self._entities_overlap(entity, existing):
                    overlaps = True
                    # If new entity has higher confidence, replace
                    if entity.confidence > existing.confidence:
                        filtered.remove(existing)
                        filtered.append(entity)
                    break
            
            if not overlaps:
                filtered.append(entity)
        
        return filtered

    def _entities_overlap(self, entity1: PIIEntity, entity2: PIIEntity) -> bool:
        """Check if two entities overlap in text."""
        return not (entity1.end <= entity2.start or entity2.end <= entity1.start)

    def detect_by_type(self, text: str, entity_type: EntityType) -> List[PIIEntity]:
        """
        Detect only specific type of PII.
        
        Args:
            text: Text to scan
            entity_type: Specific entity type to detect
        
        Returns:
            List of detected entities of specified type
        """
        # Temporarily set enabled types to just the requested type
        original_types = self.enabled_types
        self.enabled_types = {entity_type}
        self.active_patterns = {
            etype: pattern
            for etype, pattern in self.patterns.items()
            if etype in self.enabled_types
        }
        
        try:
            result = self.detect(text)
            return result.entities
        finally:
            # Restore original enabled types
            self.enabled_types = original_types
            self.active_patterns = {
                etype: pattern
                for etype, pattern in self.patterns.items()
                if etype in self.enabled_types
            }

    def get_entity_counts(self, text: str) -> dict[EntityType, int]:
        """
        Get count of each entity type in text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary mapping entity types to counts
        """
        result = self.detect(text)
        counts = defaultdict(int)
        
        for entity in result.entities:
            counts[entity.entity_type] += 1
        
        return dict(counts)

    def has_pii(self, text: str) -> bool:
        """
        Quick check if text contains any PII.
        
        Args:
            text: Text to check
        
        Returns:
            True if any PII detected, False otherwise
        """
        result = self.detect(text)
        return len(result.entities) > 0


# Convenience function
def detect_pii(
    text: str,
    enabled_types: Optional[Set[EntityType]] = None,
    min_confidence: float = 0.5,
) -> List[PIIEntity]:
    """
    Convenience function to detect PII in text.
    
    Args:
        text: Text to scan for PII
        enabled_types: Optional set of entity types to detect
        min_confidence: Minimum confidence score (0-1)
    
    Returns:
        List of detected PII entities
    
    Examples:
        >>> entities = detect_pii("My SSN is 123-45-6789")
        >>> len(entities)
        1
        >>> entities[0].entity_type
        'SSN'
    """
    detector = PIIDetector(enabled_types=enabled_types, min_confidence=min_confidence)
    result = detector.detect(text)
    return result.entities

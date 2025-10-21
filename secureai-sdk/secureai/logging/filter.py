"""
Logging Filter for automatic PII protection.

This module provides a logging filter that automatically detects and masks
PII in log messages before they are written to console, file, or other handlers.
"""

import logging
from typing import Optional

from secureai.detection.pii_detector import PIIDetector
from secureai.detection.entities import EntityType
from secureai.encryption.masker import DataMasker
from secureai.policy.manager import PolicyManager


class SecureAILogFilter(logging.Filter):
    """
    Logging filter that automatically masks PII in log messages.
    
    This filter intercepts all log messages, detects PII, and applies
    masking based on the current policy before the message is written.
    
    Examples:
        >>> import logging
        >>> from secureai.logging import SecureAILogFilter
        >>> 
        >>> # Add filter to logger
        >>> logger = logging.getLogger()
        >>> logger.addFilter(SecureAILogFilter(policy_manager))
        >>> 
        >>> # Now all logs are automatically protected
        >>> logger.info("User SSN is 123-45-6789")
        >>> # Actual output: "User SSN is ***-**-6789"
    """

    def __init__(
        self,
        policy_manager: Optional[PolicyManager] = None,
        detector: Optional[PIIDetector] = None,
        masker: Optional[DataMasker] = None,
    ):
        """
        Initialize log filter.
        
        Args:
            policy_manager: Policy manager for getting masking rules
            detector: PII detector (creates new if not provided)
            masker: Data masker (creates new if not provided)
        """
        super().__init__()
        self.policy_manager = policy_manager
        self.detector = detector or PIIDetector(min_confidence=0.5)  # Lower threshold for logs
        self.masker = masker or DataMasker()

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record, masking any PII in the message.
        
        Args:
            record: LogRecord to filter
        
        Returns:
            True (always allow the log, just modify it)
        """
        try:
            # Get the formatted message
            original_message = record.getMessage()
            
            # Detect PII in message
            detection_result = self.detector.detect(original_message)
            
            if detection_result.entity_count == 0:
                # No PII found, allow original message
                return True
            
            # Apply masking to detected entities
            protected_message = self._protect_message(
                original_message, detection_result.entities
            )
            
            # Update the record's message
            # We modify the msg and clear args to prevent double formatting
            record.msg = protected_message
            record.args = ()
            
        except Exception as e:
            # If protection fails, log the error but don't block the original log
            # This ensures logging always works even if PII detection fails
            try:
                logging.getLogger(__name__).warning(
                    f"Failed to protect log message: {e}"
                )
            except Exception:
                pass  # Avoid infinite loop
        
        return True

    def _protect_message(self, message: str, entities: list) -> str:
        """
        Protect message by masking detected PII entities.
        
        Args:
            message: Original message
            entities: List of detected PIIEntity objects
        
        Returns:
            Protected message with PII masked
        """
        protected = message
        
        # Sort entities by position (reverse) to maintain string positions
        sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)
        
        for entity in sorted_entities:
            # Get masking strategy from policy
            strategy = self._get_strategy_for_entity(entity.entity_type)
            
            # Mask the value
            masked_value = self.masker.mask(
                entity.value, strategy, entity_type=str(entity.entity_type)
            )
            
            # Replace in message
            protected = (
                protected[: entity.start] + masked_value + protected[entity.end :]
            )
        
        return protected

    def _get_strategy_for_entity(self, entity_type: EntityType):
        """
        Get masking strategy for entity type from policy.
        
        Args:
            entity_type: Type of entity
        
        Returns:
            Masking strategy to use
        """
        if self.policy_manager:
            try:
                rule = self.policy_manager.get_rule(entity_type, context="logs")
                if rule:
                    return rule.strategy
            except Exception:
                pass  # Fall back to default
        
        # Default strategies for logs
        from secureai.encryption.strategies import MaskingStrategy
        
        defaults = {
            EntityType.SSN: MaskingStrategy.PARTIAL_MASK,
            EntityType.CREDIT_CARD: MaskingStrategy.PARTIAL_MASK,
            EntityType.EMAIL: MaskingStrategy.PARTIAL_MASK,
            EntityType.PHONE: MaskingStrategy.PARTIAL_MASK,
            EntityType.IP_ADDRESS: MaskingStrategy.PARTIAL_MASK,
            EntityType.API_KEY: MaskingStrategy.FULL_MASK,
            EntityType.PASSWORD: MaskingStrategy.REDACT,
            EntityType.JWT_TOKEN: MaskingStrategy.FULL_MASK,
        }
        
        return defaults.get(entity_type, MaskingStrategy.PARTIAL_MASK)


def install_log_protection(
    policy_manager: Optional[PolicyManager] = None,
    logger: Optional[logging.Logger] = None,
) -> SecureAILogFilter:
    """
    Install log protection on a logger (or root logger).
    
    This is a convenience function to quickly add PII protection to logging.
    
    Args:
        policy_manager: Optional policy manager
        logger: Logger to protect (uses root logger if None)
    
    Returns:
        The installed filter instance
    
    Examples:
        >>> from secureai.logging import install_log_protection
        >>> 
        >>> # Protect all loggers
        >>> install_log_protection()
        >>> 
        >>> # Now all logging is automatically protected
        >>> import logging
        >>> logging.info("SSN: 123-45-6789")
        >>> # Output: "SSN: ***-**-6789"
    """
    if logger is None:
        logger = logging.getLogger()  # Root logger
    
    log_filter = SecureAILogFilter(policy_manager=policy_manager)
    logger.addFilter(log_filter)
    
    return log_filter


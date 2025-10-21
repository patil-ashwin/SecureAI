"""Regex patterns for PII detection."""

import re
from typing import Pattern

from secureai.detection.entities import EntityType


class PIIPatterns:
    """Collection of regex patterns for detecting various types of PII."""

    # Social Security Number (US)
    # Formats: 123-45-6789, 123456789
    SSN: Pattern = re.compile(
        r"\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b"
    )

    # Credit Card Numbers (major brands)
    # Visa, MasterCard, Amex, Discover, etc.
    CREDIT_CARD: Pattern = re.compile(
        r"\b(?:4\d{3}|5[1-5]\d{2}|6011|3[47]\d{2})[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
    )

    # Email addresses
    EMAIL: Pattern = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    )

    # Phone numbers (US/International)
    # Formats: (555) 123-4567, 555-123-4567, +1-555-123-4567, etc.
    PHONE: Pattern = re.compile(
        r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b"
    )

    # IPv4 addresses
    IP_ADDRESS: Pattern = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    )

    # IPv6 addresses (simplified)
    IPV6_ADDRESS: Pattern = re.compile(
        r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"
    )

    # MAC addresses
    MAC_ADDRESS: Pattern = re.compile(
        r"\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b"
    )

    # URLs
    URL: Pattern = re.compile(
        r"\b(?:https?|ftp)://[^\s/$.?#].[^\s]*\b", re.IGNORECASE
    )

    # US Zip codes
    # Formats: 12345, 12345-6789
    ZIP_CODE: Pattern = re.compile(r"\b\d{5}(?:-\d{4})?\b")

    # Dates (various formats)
    # MM/DD/YYYY, MM-DD-YYYY, YYYY-MM-DD, etc.
    DATE: Pattern = re.compile(
        r"\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b"
    )

    # Age patterns
    AGE: Pattern = re.compile(
        r"\b(?:age|aged|Age|AGE)[\s:]+(\d{1,3})(?:\s+years?(?:\s+old)?|\s+y/?o)?\b",
        re.IGNORECASE,
    )

    # API Keys / Tokens (generic patterns)
    API_KEY: Pattern = re.compile(
        r"\b(?:api[_-]?key|apikey|api[_-]?token|access[_-]?token|secret[_-]?key)"
        r"[\s:=]+['\"]?([A-Za-z0-9_\-]{20,})['\"]?\b",
        re.IGNORECASE,
    )

    # AWS Access Keys
    AWS_ACCESS_KEY: Pattern = re.compile(r"\b(AKIA[0-9A-Z]{16})\b")

    # JWT Tokens
    JWT_TOKEN: Pattern = re.compile(
        r"\beyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\b"
    )

    # Password patterns in code/config
    PASSWORD: Pattern = re.compile(
        r"\b(?:password|passwd|pwd)[\s:=]+['\"]?([^\s'\"]{4,})['\"]?\b",
        re.IGNORECASE,
    )

    # Bank Account Numbers (generic, 8-17 digits)
    BANK_ACCOUNT: Pattern = re.compile(r"\b\d{8,17}\b")

    # IBAN (International Bank Account Number)
    IBAN: Pattern = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b")

    # Passport numbers (various formats, simplified)
    PASSPORT: Pattern = re.compile(r"\b[A-Z]{1,2}\d{6,9}\b")

    # Medical Record Numbers (simplified - varies by institution)
    MEDICAL_RECORD_NUMBER: Pattern = re.compile(r"\bMRN[-\s]?:?[\s]?(\d{6,10})\b", re.IGNORECASE)

    # Coordinates (latitude/longitude)
    COORDINATES: Pattern = re.compile(
        r"\b-?\d{1,3}\.\d+,\s*-?\d{1,3}\.\d+\b"
    )

    # US State abbreviations (for context)
    US_STATE: Pattern = re.compile(
        r"\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|"
        r"MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b"
    )

    # Person names (simplified pattern - capitalized words)
    # Matches 2-4 capitalized words (First Last, First Middle Last, etc.)
    # Updated to be more inclusive for common names
    PERSON: Pattern = re.compile(
        r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b"
    )
    
    # Additional person pattern for common names (2 words minimum)
    PERSON_SIMPLE: Pattern = re.compile(
        r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b"
    )

    @classmethod
    def get_all_patterns(cls) -> dict[EntityType, Pattern]:
        """
        Get all patterns mapped to their entity types.
        
        Returns:
            Dictionary mapping EntityType to compiled regex Pattern
        """
        return {
            EntityType.SSN: cls.SSN,
            EntityType.CREDIT_CARD: cls.CREDIT_CARD,
            EntityType.EMAIL: cls.EMAIL,
            EntityType.PHONE: cls.PHONE,
            EntityType.IP_ADDRESS: cls.IP_ADDRESS,
            EntityType.MAC_ADDRESS: cls.MAC_ADDRESS,
            EntityType.URL: cls.URL,
            EntityType.ZIP_CODE: cls.ZIP_CODE,
            EntityType.DATE_OF_BIRTH: cls.DATE,
            EntityType.API_KEY: cls.API_KEY,
            EntityType.JWT_TOKEN: cls.JWT_TOKEN,
            EntityType.PASSWORD: cls.PASSWORD,
            EntityType.BANK_ACCOUNT: cls.BANK_ACCOUNT,
            EntityType.IBAN: cls.IBAN,
            EntityType.PASSPORT: cls.PASSPORT,
            EntityType.MEDICAL_RECORD_NUMBER: cls.MEDICAL_RECORD_NUMBER,
            EntityType.COORDINATES: cls.COORDINATES,
            EntityType.PERSON: cls.PERSON,
        }

    @classmethod
    def get_pattern(cls, entity_type: EntityType) -> Pattern | None:
        """
        Get pattern for a specific entity type.
        
        Args:
            entity_type: The entity type to get pattern for
        
        Returns:
            Compiled regex pattern or None if not found
        """
        return cls.get_all_patterns().get(entity_type)


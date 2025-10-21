"""Masking and encryption strategies."""

from enum import Enum


class MaskingStrategy(str, Enum):
    """Available masking/encryption strategies."""

    # Format-Preserving Encryption (reversible)
    FPE = "FPE"

    # Masking strategies (irreversible)
    PARTIAL_MASK = "PARTIAL_MASK"
    FULL_MASK = "FULL_MASK"

    # Tokenization (reversible via lookup)
    TOKENIZE = "TOKENIZE"

    # Hashing (one-way)
    HASH = "HASH"

    # Redaction (remove completely)
    REDACT = "REDACT"

    # No protection
    ALLOW = "ALLOW"

    def __str__(self) -> str:
        return self.value


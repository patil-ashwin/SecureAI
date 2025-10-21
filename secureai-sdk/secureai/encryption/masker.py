"""Data masking implementation for various masking strategies."""

import hashlib
import secrets
from typing import Optional

from secureai.encryption.strategies import MaskingStrategy
from secureai.core.exceptions import EncryptionError


class DataMasker:
    """
    Implements various data masking strategies.
    
    Supports partial masking, full masking, hashing, redaction, and tokenization.
    """

    def __init__(self, token_prefix: str = "TOK"):
        """
        Initialize data masker.
        
        Args:
            token_prefix: Prefix for generated tokens
        """
        self.token_prefix = token_prefix
        self._token_map: dict[str, str] = {}  # For tokenization lookups

    def mask(
        self,
        value: str,
        strategy: MaskingStrategy,
        entity_type: str = "default",
        show_last: int = 4,
    ) -> str:
        """
        Mask a value according to the specified strategy.
        
        Args:
            value: The value to mask
            strategy: Masking strategy to use
            entity_type: Type of entity (for context-aware masking)
            show_last: Number of characters to show for partial masking
        
        Returns:
            Masked value
            
        Raises:
            EncryptionError: If masking fails
        """
        if not value:
            return value

        try:
            if strategy == MaskingStrategy.PARTIAL_MASK:
                return self._partial_mask(value, entity_type, show_last)
            elif strategy == MaskingStrategy.FULL_MASK:
                return self._full_mask(value)
            elif strategy == MaskingStrategy.HASH:
                return self._hash(value)
            elif strategy == MaskingStrategy.REDACT:
                return self._redact(entity_type)
            elif strategy == MaskingStrategy.TOKENIZE:
                return self._tokenize(value)
            elif strategy == MaskingStrategy.ALLOW:
                return value
            else:
                raise EncryptionError(f"Unknown masking strategy: {strategy}")
                
        except Exception as e:
            raise EncryptionError(f"Masking failed: {str(e)}") from e

    def _partial_mask(self, value: str, entity_type: str, show_last: int) -> str:
        """
        Partially mask a value, showing only the last N characters.
        
        Entity-type specific logic for better UX.
        """
        length = len(value)
        
        if entity_type == "SSN":
            # SSN format: 123-45-6789 → ***-**-6789
            if "-" in value:
                parts = value.split("-")
                if len(parts) == 3:
                    return f"***-**-{parts[-1]}"
            # Fallback for non-formatted SSN
            return "*" * (length - show_last) + value[-show_last:]
        
        elif entity_type == "CREDIT_CARD":
            # Credit card: 4532-1234-5678-9010 → ****-****-****-9010
            digits = value.replace("-", "").replace(" ", "")
            last_four = digits[-4:]
            return "****-****-****-" + last_four
        
        elif entity_type == "EMAIL":
            # Email: john.smith@example.com → j***@example.com
            if "@" in value:
                local, domain = value.split("@", 1)
                if len(local) > 0:
                    return f"{local[0]}***@{domain}"
            return "*" * (length - show_last) + value[-show_last:]
        
        elif entity_type == "PHONE":
            # Phone: (555) 123-4567 → ***-***-4567
            digits = "".join(c for c in value if c.isdigit())
            if len(digits) >= 4:
                last_four = digits[-4:]
                return f"***-***-{last_four}"
            return "*" * (length - show_last) + value[-show_last:]
        
        elif entity_type == "IP_ADDRESS":
            # IP: 192.168.1.100 → 192.*.*.*
            parts = value.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.*.*.*"
            return "*" * (length - show_last) + value[-show_last:]
        
        else:
            # Default: show last N characters
            if length <= show_last:
                return "*" * length
            return "*" * (length - show_last) + value[-show_last:]

    def _full_mask(self, value: str) -> str:
        """Completely mask the value with asterisks."""
        return "*" * len(value)

    def _hash(self, value: str, length: int = 16) -> str:
        """
        Create a one-way hash of the value.
        
        Useful for deduplication and matching without revealing the original value.
        """
        hash_bytes = hashlib.sha256(value.encode()).digest()
        # Convert to hex and truncate
        return hash_bytes.hex()[:length]

    def _redact(self, entity_type: str) -> str:
        """Completely redact the value with a placeholder."""
        return f"[REDACTED_{entity_type.upper()}]"

    def _tokenize(self, value: str) -> str:
        """
        Replace value with a random token.
        
        Maintains a mapping for reverse lookup if needed.
        """
        # Check if we've already tokenized this value
        if value in self._token_map:
            return self._token_map[value]
        
        # Generate new token
        token_id = secrets.token_hex(8)
        token = f"{self.token_prefix}_{token_id}"
        
        # Store mapping
        self._token_map[value] = token
        
        return token

    def detokenize(self, token: str) -> Optional[str]:
        """
        Reverse tokenization lookup.
        
        Args:
            token: The token to look up
        
        Returns:
            Original value if found, None otherwise
        """
        # Reverse lookup
        for original, tok in self._token_map.items():
            if tok == token:
                return original
        return None

    def clear_token_map(self) -> None:
        """Clear the token mapping table."""
        self._token_map.clear()


"""Unit tests for DataMasker module."""

import pytest
from secureai.encryption.masker import DataMasker
from secureai.encryption.strategies import MaskingStrategy
from secureai.core.exceptions import EncryptionError


class TestDataMasker:
    """Test suite for DataMasker."""

    @pytest.fixture
    def masker(self) -> DataMasker:
        """Create a masker instance for testing."""
        return DataMasker()

    def test_initialization(self, masker: DataMasker) -> None:
        """Test masker initialization."""
        assert masker is not None
        assert masker.token_prefix == "TOK"

    def test_full_mask(self, masker: DataMasker) -> None:
        """Test full masking."""
        value = "123456789"
        result = masker.mask(value, MaskingStrategy.FULL_MASK)
        
        assert result == "*********"
        assert len(result) == len(value)

    def test_partial_mask_ssn(self, masker: DataMasker) -> None:
        """Test partial masking of SSN."""
        ssn = "123-45-6789"
        result = masker.mask(ssn, MaskingStrategy.PARTIAL_MASK, entity_type="SSN")
        
        assert result == "***-**-6789"
        assert result[-4:] == "6789"

    def test_partial_mask_ssn_without_dashes(self, masker: DataMasker) -> None:
        """Test partial masking of SSN without dashes."""
        ssn = "123456789"
        result = masker.mask(ssn, MaskingStrategy.PARTIAL_MASK, entity_type="SSN")
        
        # Should show last 4
        assert result.endswith("6789")
        assert "*" in result

    def test_partial_mask_credit_card(self, masker: DataMasker) -> None:
        """Test partial masking of credit card."""
        card = "4532-1234-5678-9010"
        result = masker.mask(card, MaskingStrategy.PARTIAL_MASK, entity_type="CREDIT_CARD")
        
        assert result == "****-****-****-9010"
        assert result.endswith("9010")

    def test_partial_mask_email(self, masker: DataMasker) -> None:
        """Test partial masking of email."""
        email = "john.smith@example.com"
        result = masker.mask(email, MaskingStrategy.PARTIAL_MASK, entity_type="EMAIL")
        
        assert result == "j***@example.com"
        assert "@example.com" in result
        assert result[0] == "j"

    def test_partial_mask_phone(self, masker: DataMasker) -> None:
        """Test partial masking of phone number."""
        phone = "(555) 123-4567"
        result = masker.mask(phone, MaskingStrategy.PARTIAL_MASK, entity_type="PHONE")
        
        assert "4567" in result
        assert "***" in result

    def test_partial_mask_ip_address(self, masker: DataMasker) -> None:
        """Test partial masking of IP address."""
        ip = "192.168.1.100"
        result = masker.mask(ip, MaskingStrategy.PARTIAL_MASK, entity_type="IP_ADDRESS")
        
        assert result == "192.*.*.*"
        assert result.startswith("192")

    def test_partial_mask_default(self, masker: DataMasker) -> None:
        """Test partial masking with default entity type."""
        value = "1234567890"
        result = masker.mask(value, MaskingStrategy.PARTIAL_MASK, show_last=4)
        
        assert result == "******7890"
        assert result.endswith("7890")

    def test_partial_mask_short_value(self, masker: DataMasker) -> None:
        """Test partial masking of value shorter than show_last."""
        value = "123"
        result = masker.mask(value, MaskingStrategy.PARTIAL_MASK, show_last=4)
        
        assert result == "***"
        assert len(result) == len(value)

    def test_hash_masking(self, masker: DataMasker) -> None:
        """Test hash masking."""
        value = "123456789"
        result = masker.mask(value, MaskingStrategy.HASH)
        
        assert len(result) == 16  # Default hash length
        assert result != value
        # Should be deterministic
        result2 = masker.mask(value, MaskingStrategy.HASH)
        assert result == result2

    def test_hash_different_values_produce_different_hashes(self, masker: DataMasker) -> None:
        """Test that different values produce different hashes."""
        hash1 = masker.mask("123456789", MaskingStrategy.HASH)
        hash2 = masker.mask("987654321", MaskingStrategy.HASH)
        
        assert hash1 != hash2

    def test_redact_masking(self, masker: DataMasker) -> None:
        """Test redaction."""
        value = "123-45-6789"
        result = masker.mask(value, MaskingStrategy.REDACT, entity_type="SSN")
        
        assert result == "[REDACTED_SSN]"

    def test_redact_different_entity_types(self, masker: DataMasker) -> None:
        """Test redaction with different entity types."""
        result_ssn = masker.mask("123", MaskingStrategy.REDACT, entity_type="SSN")
        result_email = masker.mask("test@test.com", MaskingStrategy.REDACT, entity_type="EMAIL")
        
        assert result_ssn == "[REDACTED_SSN]"
        assert result_email == "[REDACTED_EMAIL]"

    def test_tokenize_masking(self, masker: DataMasker) -> None:
        """Test tokenization."""
        value = "123-45-6789"
        result = masker.mask(value, MaskingStrategy.TOKENIZE)
        
        assert result.startswith("TOK_")
        assert result != value
        assert len(masker._token_map) == 1

    def test_tokenize_is_deterministic(self, masker: DataMasker) -> None:
        """Test that tokenization is deterministic for same value."""
        value = "123-45-6789"
        token1 = masker.mask(value, MaskingStrategy.TOKENIZE)
        token2 = masker.mask(value, MaskingStrategy.TOKENIZE)
        
        assert token1 == token2  # Same value should get same token

    def test_tokenize_different_values_get_different_tokens(self, masker: DataMasker) -> None:
        """Test that different values get different tokens."""
        token1 = masker.mask("value1", MaskingStrategy.TOKENIZE)
        token2 = masker.mask("value2", MaskingStrategy.TOKENIZE)
        
        assert token1 != token2

    def test_detokenize(self, masker: DataMasker) -> None:
        """Test detokenization."""
        original = "123-45-6789"
        token = masker.mask(original, MaskingStrategy.TOKENIZE)
        
        detokenized = masker.detokenize(token)
        assert detokenized == original

    def test_detokenize_unknown_token(self, masker: DataMasker) -> None:
        """Test detokenization of unknown token."""
        result = masker.detokenize("TOK_unknown")
        assert result is None

    def test_allow_strategy(self, masker: DataMasker) -> None:
        """Test allow strategy (no masking)."""
        value = "123-45-6789"
        result = masker.mask(value, MaskingStrategy.ALLOW)
        
        assert result == value  # Should be unchanged

    def test_empty_value(self, masker: DataMasker) -> None:
        """Test masking of empty string."""
        result = masker.mask("", MaskingStrategy.FULL_MASK)
        assert result == ""

    def test_clear_token_map(self, masker: DataMasker) -> None:
        """Test clearing token map."""
        masker.mask("value1", MaskingStrategy.TOKENIZE)
        masker.mask("value2", MaskingStrategy.TOKENIZE)
        
        assert len(masker._token_map) == 2
        
        masker.clear_token_map()
        assert len(masker._token_map) == 0

    def test_custom_token_prefix(self) -> None:
        """Test masker with custom token prefix."""
        masker = DataMasker(token_prefix="CUSTOM")
        token = masker.mask("value", MaskingStrategy.TOKENIZE)
        
        assert token.startswith("CUSTOM_")

    @pytest.mark.parametrize(
        "value,strategy,entity_type,expected_pattern",
        [
            ("123-45-6789", MaskingStrategy.PARTIAL_MASK, "SSN", r"\*\*\*-\*\*-\d{4}"),
            ("test@example.com", MaskingStrategy.PARTIAL_MASK, "EMAIL", r"t\*\*\*@example\.com"),
            ("192.168.1.100", MaskingStrategy.PARTIAL_MASK, "IP_ADDRESS", r"192\.\*\.\*\.\*"),
            ("anything", MaskingStrategy.FULL_MASK, "DEFAULT", r"\*+"),
            ("anything", MaskingStrategy.REDACT, "TEST", r"\[REDACTED_TEST\]"),
        ],
    )
    def test_mask_patterns(
        self,
        masker: DataMasker,
        value: str,
        strategy: MaskingStrategy,
        entity_type: str,
        expected_pattern: str,
    ) -> None:
        """Test various masking patterns."""
        import re
        
        result = masker.mask(value, strategy, entity_type)
        assert re.match(expected_pattern, result) is not None

    def test_unknown_strategy_raises_error(self, masker: DataMasker) -> None:
        """Test that unknown strategy raises error."""
        # Create an invalid strategy by manipulating the enum
        with pytest.raises(EncryptionError):
            masker.mask("value", "INVALID_STRATEGY")  # type: ignore


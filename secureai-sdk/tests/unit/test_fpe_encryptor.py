"""Unit tests for FPE encryption module."""

import pytest
from secureai.encryption.fpe import FPEEncryptor
from secureai.core.exceptions import EncryptionError


class TestFPEEncryptor:
    """Test suite for FPEEncryptor."""

    @pytest.fixture
    def encryptor(self) -> FPEEncryptor:
        """Create an encryptor instance for testing."""
        return FPEEncryptor(key="test-secret-key")

    def test_initialization(self, encryptor: FPEEncryptor) -> None:
        """Test encryptor initialization."""
        assert encryptor is not None
        assert encryptor.key is not None
        assert len(encryptor.key) == 32  # 256-bit key

    def test_encrypt_ssn_preserves_format(self, encryptor: FPEEncryptor) -> None:
        """Test that SSN encryption preserves format."""
        ssn = "123-45-6789"
        encrypted = encryptor.encrypt(ssn, "SSN")
        
        # Should maintain format: XXX-XX-XXXX
        assert len(encrypted) == len(ssn)
        assert encrypted[3] == "-"
        assert encrypted[6] == "-"
        assert encrypted != ssn  # Should be different
        assert all(c.isdigit() or c == "-" for c in encrypted)

    def test_encrypt_empty_string(self, encryptor: FPEEncryptor) -> None:
        """Test encryption of empty string."""
        result = encryptor.encrypt("", "SSN")
        assert result == ""

    def test_encrypt_credit_card_preserves_format(self, encryptor: FPEEncryptor) -> None:
        """Test that credit card encryption preserves format."""
        card = "4532-1234-5678-9010"
        encrypted = encryptor.encrypt(card, "CREDIT_CARD")
        
        # Should maintain format with dashes
        assert len(encrypted) == len(card)
        assert encrypted[4] == "-"
        assert encrypted[9] == "-"
        assert encrypted[14] == "-"
        assert encrypted != card

    def test_encrypt_is_deterministic(self, encryptor: FPEEncryptor) -> None:
        """Test that encryption is deterministic (same input → same output)."""
        ssn = "123-45-6789"
        encrypted1 = encryptor.encrypt(ssn, "SSN")
        encrypted2 = encryptor.encrypt(ssn, "SSN")
        
        assert encrypted1 == encrypted2  # Must be deterministic

    def test_encrypt_different_entity_types_produce_different_results(
        self, encryptor: FPEEncryptor
    ) -> None:
        """Test that same value with different entity types produces different results."""
        value = "123456789"
        encrypted_ssn = encryptor.encrypt(value, "SSN")
        encrypted_id = encryptor.encrypt(value, "ID")
        
        # Different entity types should produce different ciphertexts
        assert encrypted_ssn != encrypted_id

    def test_encrypt_maintains_character_types(self, encryptor: FPEEncryptor) -> None:
        """Test that digits remain digits, letters remain letters."""
        text = "ABC123"
        encrypted = encryptor.encrypt(text, "DEFAULT")
        
        # First 3 should be letters, last 3 should be digits
        assert encrypted[:3].isalpha()
        assert encrypted[3:].isdigit()
        assert encrypted != text

    def test_encrypt_preserves_special_characters(self, encryptor: FPEEncryptor) -> None:
        """Test that special characters remain in their positions."""
        value = "123-45-6789"
        encrypted = encryptor.encrypt(value, "SSN")
        
        # Dashes should stay in the same positions
        assert encrypted[3] == "-"
        assert encrypted[6] == "-"

    def test_encrypt_case_preservation(self, encryptor: FPEEncryptor) -> None:
        """Test that uppercase/lowercase is preserved."""
        text = "JohnSmith"
        encrypted = encryptor.encrypt(text, "NAME")
        
        # Check that first char is upper, rest follow pattern
        assert encrypted[0].isupper()
        assert encrypted[4].isupper()  # S in Smith

    def test_cache_works(self, encryptor: FPEEncryptor) -> None:
        """Test that caching works for performance."""
        ssn = "123-45-6789"
        
        # First encryption
        encrypted1 = encryptor.encrypt(ssn, "SSN")
        
        # Should be cached
        cache_key = "SSN:123-45-6789"
        assert cache_key in encryptor._cache
        
        # Second encryption should use cache
        encrypted2 = encryptor.encrypt(ssn, "SSN")
        assert encrypted1 == encrypted2

    def test_clear_cache(self, encryptor: FPEEncryptor) -> None:
        """Test cache clearing."""
        encryptor.encrypt("123-45-6789", "SSN")
        assert len(encryptor._cache) > 0
        
        encryptor.clear_cache()
        assert len(encryptor._cache) == 0

    def test_encrypt_with_tweak(self) -> None:
        """Test encryption with custom tweak."""
        encryptor1 = FPEEncryptor(key="test-key", tweak="tweak1")
        encryptor2 = FPEEncryptor(key="test-key", tweak="tweak2")
        
        ssn = "123-45-6789"
        encrypted1 = encryptor1.encrypt(ssn, "SSN")
        encrypted2 = encryptor2.encrypt(ssn, "SSN")
        
        # Different tweaks should produce different results
        assert encrypted1 != encrypted2

    def test_encrypt_email_preserves_format(self, encryptor: FPEEncryptor) -> None:
        """Test that email encryption preserves general structure."""
        email = "john.smith@example.com"
        encrypted = encryptor.encrypt(email, "EMAIL")
        
        # Should maintain @ symbol
        assert "@" in encrypted
        assert "." in encrypted
        assert encrypted != email

    def test_encrypt_phone_preserves_format(self, encryptor: FPEEncryptor) -> None:
        """Test that phone number encryption preserves format."""
        phone = "(555) 123-4567"
        encrypted = encryptor.encrypt(phone, "PHONE")
        
        # Should maintain special characters
        assert encrypted[0] == "("
        assert encrypted[4] == ")"
        assert encrypted != phone

    @pytest.mark.parametrize(
        "value,entity_type",
        [
            ("123-45-6789", "SSN"),
            ("4532-1234-5678-9010", "CREDIT_CARD"),
            ("john@example.com", "EMAIL"),
            ("192.168.1.100", "IP_ADDRESS"),
            ("ABC123XYZ", "DEFAULT"),
        ],
    )
    def test_encrypt_various_formats(
        self, encryptor: FPEEncryptor, value: str, entity_type: str
    ) -> None:
        """Test encryption of various data formats."""
        encrypted = encryptor.encrypt(value, entity_type)
        
        # Basic assertions
        assert encrypted is not None
        assert len(encrypted) == len(value)
        assert encrypted != value  # Should be different (unless very unlucky!)

    def test_extract_structure(self, encryptor: FPEEncryptor) -> None:
        """Test structure extraction."""
        text = "ABC-123"
        structure, chars = encryptor._extract_structure(text)
        
        assert len(structure) == 7
        assert chars == "ABC123"
        
        # Check structure contains correct types
        assert structure[0] == (0, "upper", "A")
        assert structure[3] == (3, "special", "-")
        assert structure[4] == (4, "digit", "1")

    def test_rebuild_with_structure(self, encryptor: FPEEncryptor) -> None:
        """Test rebuilding string with structure."""
        text = "ABC-123"
        structure, chars = encryptor._extract_structure(text)
        
        # Rebuild should give original
        rebuilt = encryptor._rebuild_with_structure(structure, chars)
        assert rebuilt == text

    def test_encryption_with_no_encryptable_chars(self, encryptor: FPEEncryptor) -> None:
        """Test encryption of text with only special characters."""
        text = "---***"
        encrypted = encryptor.encrypt(text, "DEFAULT")
        
        # Should return unchanged since no encryptable characters
        assert encrypted == text


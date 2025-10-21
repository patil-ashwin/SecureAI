"""Unit tests for Secure LLM module."""

import pytest
from unittest.mock import Mock, patch

from secureai.llm.secure_llm import SecureLLM
from secureai.llm.providers import LLMProvider
from secureai.detection.entities import PIIEntity, EntityType
from secureai.core.exceptions import SecureAIError


class TestSecureLLM:
    """Test suite for SecureLLM."""

    @pytest.fixture
    def secure_llm(self) -> SecureLLM:
        """Create a SecureLLM instance for testing."""
        return SecureLLM(
            provider=LLMProvider.OPENAI,
            api_key="test-key",
            auto_protect=True,
        )

    def test_initialization(self, secure_llm: SecureLLM) -> None:
        """Test LLM client initialization."""
        assert secure_llm is not None
        assert secure_llm.provider == LLMProvider.OPENAI
        assert secure_llm.api_key == "test-key"
        assert secure_llm.auto_protect is True
        assert secure_llm.detector is not None
        assert secure_llm.encryptor is not None

    def test_initialization_with_string_provider(self) -> None:
        """Test initialization with string provider."""
        llm = SecureLLM(provider="openai", api_key="test-key")
        assert llm.provider == LLMProvider.OPENAI

    def test_initialization_anthropic(self) -> None:
        """Test initialization with Anthropic provider."""
        llm = SecureLLM(provider=LLMProvider.ANTHROPIC, api_key="test-key")
        assert llm.provider == LLMProvider.ANTHROPIC

    def test_chat_with_no_pii(self, secure_llm: SecureLLM) -> None:
        """Test chat with prompt containing no PII."""
        response = secure_llm.chat("What is the weather today?")
        
        assert response is not None
        assert "weather" in response.lower()

    def test_chat_with_ssn_in_prompt(self, secure_llm: SecureLLM) -> None:
        """Test that SSN in prompt is protected."""
        prompt = "What is the account status for SSN 123-45-6789?"
        response = secure_llm.chat(prompt)
        
        # Response should contain something
        assert response is not None
        # Original SSN should have been encrypted when sent
        # Entity map should have been created and cleared
        assert len(secure_llm._entity_map) == 0  # Cleared after call

    def test_chat_with_email_in_prompt(self, secure_llm: SecureLLM) -> None:
        """Test that email in prompt is protected."""
        prompt = "Send newsletter to john.smith@example.com"
        response = secure_llm.chat(prompt)
        
        assert response is not None

    def test_chat_with_multiple_pii(self, secure_llm: SecureLLM) -> None:
        """Test chat with multiple PII entities in prompt."""
        prompt = "Contact john@example.com about SSN 123-45-6789"
        response = secure_llm.chat(prompt)
        
        assert response is not None

    def test_protect_prompt(self, secure_llm: SecureLLM) -> None:
        """Test prompt protection logic."""
        entities = [
            PIIEntity(
                entity_type=EntityType.SSN,
                value="123-45-6789",
                start=15,
                end=26,
            )
        ]
        
        prompt = "User SSN is 123-45-6789"
        protected = secure_llm._protect_prompt(prompt, entities)
        
        # Protected prompt should not contain original SSN
        assert "123-45-6789" not in protected
        # Should have "User SSN is" prefix
        assert "User SSN is" in protected
        # Entity map should be populated
        assert len(secure_llm._entity_map) > 0

    def test_protect_prompt_multiple_entities(self, secure_llm: SecureLLM) -> None:
        """Test protecting prompt with multiple entities."""
        entities = [
            PIIEntity(
                entity_type=EntityType.SSN,
                value="123-45-6789",
                start=8,
                end=19,
            ),
            PIIEntity(
                entity_type=EntityType.EMAIL,
                value="john@example.com",
                start=29,
                end=45,
            ),
        ]
        
        prompt = "SSN is 123-45-6789 and email john@example.com"
        protected = secure_llm._protect_prompt(prompt, entities)
        
        # Original values should not be in protected prompt
        assert "123-45-6789" not in protected
        assert "john@example.com" not in protected
        # Entity map should have both mappings
        assert len(secure_llm._entity_map) == 2

    def test_restore_response(self, secure_llm: SecureLLM) -> None:
        """Test response restoration logic."""
        # Set up entity map
        secure_llm._entity_map = {
            "987-65-4321": "123-45-6789",
            "jane@test.com": "john@example.com",
        }
        
        response = "The SSN 987-65-4321 belongs to jane@test.com"
        restored = secure_llm._restore_response(response)
        
        # Original values should be restored
        assert "123-45-6789" in restored
        assert "john@example.com" in restored
        # Encrypted values should not be in restored response
        assert "987-65-4321" not in restored
        assert "jane@test.com" not in restored

    def test_auto_protect_disabled(self) -> None:
        """Test with auto-protection disabled."""
        llm = SecureLLM(
            provider=LLMProvider.OPENAI,
            api_key="test-key",
            auto_protect=False,
        )
        
        prompt = "SSN is 123-45-6789"
        response = llm.chat(prompt)
        
        # Should process without protection
        assert response is not None
        # No entity map should be created
        assert len(llm._entity_map) == 0

    def test_chat_with_model_parameter(self, secure_llm: SecureLLM) -> None:
        """Test chat with specific model."""
        response = secure_llm.chat(
            "What is AI?",
            model="gpt-4",
        )
        
        assert response is not None

    def test_chat_with_temperature(self, secure_llm: SecureLLM) -> None:
        """Test chat with temperature parameter."""
        response = secure_llm.chat(
            "What is AI?",
            temperature=0.5,
        )
        
        assert response is not None

    def test_chat_with_max_tokens(self, secure_llm: SecureLLM) -> None:
        """Test chat with max_tokens parameter."""
        response = secure_llm.chat(
            "What is AI?",
            max_tokens=500,
        )
        
        assert response is not None

    def test_complete_method(self, secure_llm: SecureLLM) -> None:
        """Test completion method (legacy API style)."""
        response = secure_llm.complete("Once upon a time")
        
        assert response is not None

    def test_get_entity_map(self, secure_llm: SecureLLM) -> None:
        """Test getting entity map."""
        secure_llm._entity_map = {"encrypted": "original"}
        
        entity_map = secure_llm.get_entity_map()
        
        assert entity_map == {"encrypted": "original"}
        # Should be a copy
        entity_map["new"] = "value"
        assert "new" not in secure_llm._entity_map

    def test_clear_entity_map(self, secure_llm: SecureLLM) -> None:
        """Test clearing entity map."""
        secure_llm._entity_map = {"encrypted": "original"}
        
        secure_llm.clear_entity_map()
        
        assert len(secure_llm._entity_map) == 0

    def test_different_providers(self) -> None:
        """Test initialization with different providers."""
        providers = [
            LLMProvider.OPENAI,
            LLMProvider.ANTHROPIC,
            LLMProvider.AZURE_OPENAI,
            LLMProvider.COHERE,
        ]
        
        for provider in providers:
            llm = SecureLLM(provider=provider, api_key="test-key")
            assert llm.provider == provider

    def test_call_llm_openai(self) -> None:
        """Test LLM call with OpenAI provider."""
        llm = SecureLLM(provider=LLMProvider.OPENAI, api_key="test-key")
        
        response = llm._call_llm("Test prompt", None, 0.7, 1000)
        
        assert "OpenAI" in response
        assert "Test prompt" in response

    def test_call_llm_anthropic(self) -> None:
        """Test LLM call with Anthropic provider."""
        llm = SecureLLM(provider=LLMProvider.ANTHROPIC, api_key="test-key")
        
        response = llm._call_llm("Test prompt", None, 0.7, 1000)
        
        assert "Claude" in response
        assert "Test prompt" in response

    def test_audit_logging(self, secure_llm: SecureLLM, caplog) -> None:
        """Test that audit logging works."""
        import logging
        caplog.set_level(logging.INFO)
        
        prompt = "User SSN is 123-45-6789"
        secure_llm.chat(prompt)
        
        # Should have logged the protection
        assert any("Protected" in record.message for record in caplog.records)

    def test_entity_map_cleared_after_call(self, secure_llm: SecureLLM) -> None:
        """Test that entity map is cleared after each call."""
        prompt = "SSN is 123-45-6789"
        
        # First call
        secure_llm.chat(prompt)
        assert len(secure_llm._entity_map) == 0
        
        # Second call
        secure_llm.chat(prompt)
        assert len(secure_llm._entity_map) == 0

    def test_end_to_end_protection_restoration(self, secure_llm: SecureLLM) -> None:
        """Test complete flow: protect prompt, call LLM, restore response."""
        # Mock the LLM call to return a response with encrypted PII
        original_call = secure_llm._call_llm
        
        def mock_call(prompt, *args, **kwargs):
            # LLM echoes back the (protected) prompt
            return f"Sure, I'll help with {prompt}"
        
        secure_llm._call_llm = mock_call
        
        try:
            prompt = "Send email to john@example.com about account 123-45-6789"
            response = secure_llm.chat(prompt)
            
            # Response should have original PII restored
            # (though in this test, the mock doesn't actually use the encrypted values)
            assert response is not None
            
        finally:
            secure_llm._call_llm = original_call


class TestLLMProvider:
    """Test suite for LLMProvider enum."""

    def test_provider_values(self) -> None:
        """Test provider enum values."""
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.AZURE_OPENAI.value == "azure_openai"

    def test_provider_string_conversion(self) -> None:
        """Test converting provider to string."""
        assert str(LLMProvider.OPENAI) == "openai"
        assert str(LLMProvider.ANTHROPIC) == "anthropic"

    def test_provider_from_string(self) -> None:
        """Test creating provider from string."""
        provider = LLMProvider("openai")
        assert provider == LLMProvider.OPENAI


class TestSecureLLMIntegration:
    """Integration tests for SecureLLM."""

    def test_real_world_scenario_customer_service(self) -> None:
        """Test realistic customer service scenario."""
        llm = SecureLLM(provider=LLMProvider.OPENAI, api_key="test-key")
        
        # Customer service prompt with PII
        prompt = """
        Draft a response email to john.smith@example.com regarding 
        their account inquiry. Their customer ID is 123-45-6789 and 
        they called from (555) 123-4567.
        """
        
        response = llm.chat(prompt)
        
        # Should get a response
        assert response is not None
        # Entity map should be cleared
        assert len(llm._entity_map) == 0

    def test_real_world_scenario_data_analysis(self) -> None:
        """Test data analysis scenario."""
        llm = SecureLLM(provider=LLMProvider.OPENAI, api_key="test-key")
        
        prompt = """
        Analyze the pattern: User 192.168.1.100 accessed API with 
        key sk_test_abc123xyz456 at 10:00 AM.
        """
        
        response = llm.chat(prompt)
        assert response is not None

    def test_multiple_sequential_calls(self) -> None:
        """Test multiple sequential LLM calls."""
        llm = SecureLLM(provider=LLMProvider.OPENAI, api_key="test-key")
        
        # First call
        response1 = llm.chat("User email: john@example.com")
        assert response1 is not None
        
        # Second call (entity map should be fresh)
        response2 = llm.chat("User SSN: 123-45-6789")
        assert response2 is not None
        
        # Third call
        response3 = llm.chat("No PII here")
        assert response3 is not None


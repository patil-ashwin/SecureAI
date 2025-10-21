"""
Secure LLM Client.

Provides automatic PII protection for LLM API calls (OpenAI, Anthropic, etc.).
"""

from typing import Optional, Dict, Any, List
import logging

from secureai.llm.providers import LLMProvider
from secureai.detection.pii_detector import PIIDetector
from secureai.detection.entities import PIIEntity
from secureai.encryption.fpe import FPEEncryptor
from secureai.encryption.masker import DataMasker
from secureai.policy.manager import PolicyManager
from secureai.core.exceptions import SecureAIError

logger = logging.getLogger(__name__)


class SecureLLM:
    """
    Secure LLM client that automatically protects PII in prompts.
    
    This client wraps LLM API calls (OpenAI, Anthropic, etc.) and:
    1. Detects PII in prompts before sending to LLM
    2. Encrypts PII using FPE (format-preserving encryption)
    3. Sends protected prompt to LLM
    4. Decrypts PII in LLM response
    5. Returns response with original values restored
    6. Logs all operations for audit
    
    Examples:
        >>> from secureai.llm import SecureLLM
        >>> 
        >>> llm = SecureLLM(provider="openai", api_key="sk-...")
        >>> response = llm.chat("Summarize John Smith's account")
        >>> # PII automatically protected before sending to OpenAI
    """

    def __init__(
        self,
        provider: LLMProvider | str = LLMProvider.OPENAI,
        api_key: Optional[str] = None,
        policy_manager: Optional[PolicyManager] = None,
        detector: Optional[PIIDetector] = None,
        encryptor: Optional[FPEEncryptor] = None,
        masker: Optional[DataMasker] = None,
        auto_protect: bool = True,
        audit_log: bool = True,
    ):
        """
        Initialize Secure LLM client.
        
        Args:
            provider: LLM provider (openai, anthropic, etc.)
            api_key: API key for the LLM provider
            policy_manager: Optional policy manager for rules
            detector: Optional PII detector (creates new if not provided)
            encryptor: Optional FPE encryptor (creates new if not provided)
            masker: Optional data masker (creates new if not provided)
            auto_protect: Automatically protect PII in prompts
            audit_log: Log all LLM interactions for audit
        """
        self.provider = LLMProvider(provider) if isinstance(provider, str) else provider
        self.api_key = api_key
        self.policy_manager = policy_manager
        self.auto_protect = auto_protect
        self.audit_log = audit_log
        
        # Initialize components
        self.detector = detector or PIIDetector(min_confidence=0.6)
        self.encryptor = encryptor or FPEEncryptor(key=api_key or "default-key")
        self.masker = masker or DataMasker()
        
        # Entity mapping for decryption (prompt PII -> encrypted PII)
        self._entity_map: Dict[str, str] = {}
        
        # Initialize provider-specific client
        self._client: Optional[Any] = None
        self._initialize_provider_client()

    def _initialize_provider_client(self) -> None:
        """Initialize the provider-specific LLM client."""
        # This is a stub - in production would initialize actual clients
        # For now, we'll use mock clients for testing
        if self.provider == LLMProvider.OPENAI:
            # try:
            #     import openai
            #     openai.api_key = self.api_key
            #     self._client = openai
            # except ImportError:
            #     logger.warning("OpenAI library not installed")
            pass
        elif self.provider == LLMProvider.ANTHROPIC:
            # try:
            #     import anthropic
            #     self._client = anthropic.Anthropic(api_key=self.api_key)
            # except ImportError:
            #     logger.warning("Anthropic library not installed")
            pass

    def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> str:
        """
        Send a chat message to the LLM with automatic PII protection.
        
        Args:
            prompt: User prompt/message
            model: Model to use (e.g., "gpt-4", "claude-3-opus")
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLM response with PII restored
        
        Examples:
            >>> llm = SecureLLM(provider="openai")
            >>> response = llm.chat("Write email to john@example.com")
            >>> # Email address encrypted before sending to OpenAI
        """
        try:
            # Step 1: Detect PII in prompt
            if self.auto_protect:
                detected_entities = self.detector.detect(prompt)
                
                if detected_entities.entity_count > 0:
                    # Step 2: Protect the prompt
                    protected_prompt = self._protect_prompt(prompt, detected_entities.entities)
                    
                    if self.audit_log:
                        logger.info(
                            f"Protected {detected_entities.entity_count} entities in prompt"
                        )
                else:
                    protected_prompt = prompt
            else:
                protected_prompt = prompt
            
            # Step 3: Call LLM with protected prompt
            llm_response = self._call_llm(protected_prompt, model, temperature, max_tokens, **kwargs)
            
            # Step 4: Restore PII in response
            if self.auto_protect and self._entity_map:
                restored_response = self._restore_response(llm_response)
            else:
                restored_response = llm_response
            
            # Step 5: Clear entity map for next call
            self._entity_map.clear()
            
            return restored_response
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise SecureAIError(f"Secure LLM call failed: {e}") from e

    def _protect_prompt(self, prompt: str, entities: List[PIIEntity]) -> str:
        """
        Protect prompt by encrypting detected PII.
        
        Args:
            prompt: Original prompt
            entities: Detected PII entities
        
        Returns:
            Protected prompt with PII encrypted
        """
        protected = prompt
        
        # Sort entities by position (reverse) to maintain string positions
        sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)
        
        for entity in sorted_entities:
            # Encrypt the entity value using FPE
            encrypted_value = self.encryptor.encrypt(
                entity.value, str(entity.entity_type)
            )
            
            # Store mapping for later restoration
            self._entity_map[encrypted_value] = entity.value
            
            # Replace in prompt
            protected = (
                protected[: entity.start] + encrypted_value + protected[entity.end :]
            )
        
        return protected

    def _restore_response(self, response: str) -> str:
        """
        Restore original PII values in LLM response.
        
        Args:
            response: LLM response with encrypted PII
        
        Returns:
            Response with original PII restored
        """
        restored = response
        
        # Replace encrypted values with original values
        for encrypted, original in self._entity_map.items():
            restored = restored.replace(encrypted, original)
        
        return restored

    def _call_llm(
        self,
        prompt: str,
        model: Optional[str],
        temperature: float,
        max_tokens: int,
        **kwargs: Any,
    ) -> str:
        """
        Call the LLM provider API.
        
        This is a stub implementation - in production would call actual APIs.
        
        Args:
            prompt: Prompt to send
            model: Model to use
            temperature: Temperature setting
            max_tokens: Max tokens
            **kwargs: Additional parameters
        
        Returns:
            LLM response
        """
        # For testing, echo back the prompt with a prefix
        # In production, this would call the actual LLM API
        
        if self.provider == LLMProvider.OPENAI:
            # Mock OpenAI response
            return f"OpenAI response to: {prompt}"
        elif self.provider == LLMProvider.ANTHROPIC:
            # Mock Anthropic response
            return f"Claude response to: {prompt}"
        else:
            return f"Response to: {prompt}"

    def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Text completion (legacy API style).
        
        Args:
            prompt: Prompt for completion
            model: Model to use
            **kwargs: Additional parameters
        
        Returns:
            Completion text
        """
        return self.chat(prompt, model=model, **kwargs)

    def get_entity_map(self) -> Dict[str, str]:
        """
        Get current entity mapping (for debugging).
        
        Returns:
            Dictionary mapping encrypted values to original values
        """
        return self._entity_map.copy()

    def clear_entity_map(self) -> None:
        """Clear the entity mapping."""
        self._entity_map.clear()


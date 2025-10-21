"""Main SecureAI client."""

from typing import Optional, Dict, Any
from secureai.core.exceptions import ConfigurationError


class SecureAI:
    """
    Main SecureAI SDK client.
    
    This is the entry point for initializing and configuring the SDK.
    """

    _instance: Optional["SecureAI"] = None
    _initialized: bool = False

    def __init__(
        self,
        api_key: str,
        app_id: Optional[str] = None,
        auto_protect_logs: bool = False,
        policies: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize SecureAI client.
        
        Args:
            api_key: API key for SecureAI platform
            app_id: Application identifier
            auto_protect_logs: Automatically protect logging output
            policies: Optional local policy overrides
        """
        self.api_key = api_key
        self.app_id = app_id or "default"
        self.auto_protect_logs = auto_protect_logs
        self.policies = policies or {}

    @classmethod
    def init(
        cls,
        api_key: str,
        app_id: Optional[str] = None,
        auto_protect_logs: bool = False,
        policies: Optional[Dict[str, Any]] = None,
    ) -> "SecureAI":
        """
        Initialize the SecureAI SDK (singleton pattern).
        
        Args:
            api_key: API key for SecureAI platform
            app_id: Application identifier
            auto_protect_logs: Automatically protect logging output
            policies: Optional local policy overrides
        
        Returns:
            Initialized SecureAI instance
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not api_key:
            raise ConfigurationError("API key is required")

        if cls._instance is None:
            cls._instance = cls(api_key, app_id, auto_protect_logs, policies)
            cls._initialized = True

        return cls._instance

    @classmethod
    def get_instance(cls) -> Optional["SecureAI"]:
        """Get the current SecureAI instance."""
        return cls._instance

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if SecureAI has been initialized."""
        return cls._initialized


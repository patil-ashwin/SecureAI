"""Custom exceptions for SecureAI SDK."""


class SecureAIError(Exception):
    """Base exception for all SecureAI errors."""

    pass


class ConfigurationError(SecureAIError):
    """Raised when there's a configuration issue."""

    pass


class EncryptionError(SecureAIError):
    """Raised when encryption/decryption fails."""

    pass


class DetectionError(SecureAIError):
    """Raised when PII detection fails."""

    pass


class PolicyError(SecureAIError):
    """Raised when policy-related operations fail."""

    pass


class NetworkError(SecureAIError):
    """Raised when network operations fail."""

    pass


class AuthenticationError(SecureAIError):
    """Raised when authentication fails."""

    pass


class ValidationError(SecureAIError):
    """Raised when validation fails."""

    pass


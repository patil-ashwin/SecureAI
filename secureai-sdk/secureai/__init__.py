"""
SecureAI Python SDK - AI Privacy Protection Platform

Protect sensitive data in AI/ML workloads with Format-Preserving Encryption (FPE).
"""

__version__ = "0.1.0"

from secureai.core.client import SecureAI
from secureai.core.exceptions import (
    SecureAIError,
    ConfigurationError,
    EncryptionError,
    DetectionError,
    PolicyError,
)
from secureai.detection.pii_detector import detect_pii
from secureai.core.protection import protect, restore
from secureai.encryption.strategies import MaskingStrategy

__all__ = [
    # Main client
    "SecureAI",
    # Core functions
    "detect_pii",
    "protect",
    "restore",
    # Enums
    "MaskingStrategy",
    # Exceptions
    "SecureAIError",
    "ConfigurationError",
    "EncryptionError",
    "DetectionError",
    "PolicyError",
]


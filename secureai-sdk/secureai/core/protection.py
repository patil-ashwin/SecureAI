"""Core protection functions - stubs for now."""

from typing import Optional


def protect(text: str, context: Optional[str] = None) -> str:
    """
    Protect PII in text.
    
    Args:
        text: Text to protect
        context: Optional context for policy application
    
    Returns:
        Protected text
    """
    # Stub - will be implemented fully later
    return text


def restore(text: str, context: Optional[str] = None) -> str:
    """
    Restore original values from protected text.
    
    Args:
        text: Protected text
        context: Optional context
    
    Returns:
        Restored text
    """
    # Stub - will be implemented fully later
    return text


"""Unit tests for logging filter."""

import pytest
import logging
from io import StringIO
from unittest.mock import Mock, patch

from secureai.logging.filter import SecureAILogFilter, install_log_protection
from secureai.detection.entities import EntityType
from secureai.encryption.strategies import MaskingStrategy
from secureai.policy.manager import PolicyManager
from secureai.policy.models import Policy, MaskingRule


class TestSecureAILogFilter:
    """Test suite for SecureAILogFilter."""

    @pytest.fixture
    def log_filter(self) -> SecureAILogFilter:
        """Create a log filter for testing."""
        return SecureAILogFilter()

    @pytest.fixture
    def logger_with_filter(self, log_filter: SecureAILogFilter) -> logging.Logger:
        """Create a logger with filter attached."""
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.filters.clear()
        
        # Add string handler to capture output
        string_handler = logging.StreamHandler(StringIO())
        string_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(string_handler)
        
        # Add our filter
        logger.addFilter(log_filter)
        
        return logger

    def test_filter_initialization(self, log_filter: SecureAILogFilter) -> None:
        """Test filter initialization."""
        assert log_filter is not None
        assert log_filter.detector is not None
        assert log_filter.masker is not None

    def test_filter_with_no_pii(self, logger_with_filter: logging.Logger) -> None:
        """Test filter with message containing no PII."""
        handler = logger_with_filter.handlers[0]
        stream = handler.stream
        
        logger_with_filter.info("This is a normal log message")
        
        output = stream.getvalue()
        assert "This is a normal log message" in output

    def test_filter_masks_ssn(self, logger_with_filter: logging.Logger) -> None:
        """Test that SSN is masked in logs."""
        handler = logger_with_filter.handlers[0]
        stream = handler.stream
        
        logger_with_filter.info("User SSN is 123-45-6789")
        
        output = stream.getvalue()
        assert "123-45-6789" not in output  # Original not in output
        assert "***-**-6789" in output or "*" in output  # Masked version

    def test_filter_masks_email(self, logger_with_filter: logging.Logger) -> None:
        """Test that email is masked in logs."""
        handler = logger_with_filter.handlers[0]
        stream = handler.stream
        
        logger_with_filter.info("Contact: john.smith@example.com")
        
        output = stream.getvalue()
        assert "john.smith@example.com" not in output
        assert "@example.com" in output  # Domain should be visible

    def test_filter_masks_credit_card(self, logger_with_filter: logging.Logger) -> None:
        """Test that credit card is masked in logs."""
        handler = logger_with_filter.handlers[0]
        stream = handler.stream
        
        logger_with_filter.info("Card: 4532-1234-5678-9010")
        
        output = stream.getvalue()
        assert "4532-1234-5678-9010" not in output
        assert "9010" in output or "*" in output  # Last 4 or masked

    def test_filter_masks_multiple_pii(self, logger_with_filter: logging.Logger) -> None:
        """Test masking multiple PII in one message."""
        handler = logger_with_filter.handlers[0]
        stream = handler.stream
        
        logger_with_filter.info("User SSN: 123-45-6789, Email: test@example.com")
        
        output = stream.getvalue()
        assert "123-45-6789" not in output
        assert "test@example.com" not in output
        assert "*" in output  # Some masking occurred

    def test_filter_with_policy_manager(self) -> None:
        """Test filter using policy manager for rules."""
        policy = Policy(
            policy_id="test",
            name="Test",
            rules=[
                MaskingRule(
                    entity_type=EntityType.SSN,
                    strategy=MaskingStrategy.FULL_MASK,
                    contexts=["logs"],
                )
            ],
        )
        
        with patch.object(PolicyManager, "_fetch_policy"):
            policy_manager = PolicyManager(
                api_key="test", sync_interval=0, fallback_policy=policy
            )
            policy_manager._policy = policy
        
        log_filter = SecureAILogFilter(policy_manager=policy_manager)
        
        logger = logging.getLogger("test_policy_logger")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.filters.clear()
        
        string_handler = logging.StreamHandler(StringIO())
        string_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(string_handler)
        logger.addFilter(log_filter)
        
        logger.info("SSN: 123-45-6789")
        
        output = string_handler.stream.getvalue()
        assert "123-45-6789" not in output
        # Full mask should be all asterisks
        assert "*" in output

    def test_filter_record_modification(self, log_filter: SecureAILogFilter) -> None:
        """Test that filter modifies log record correctly."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="User SSN is %s",
            args=("123-45-6789",),
            exc_info=None,
        )
        
        # Filter the record
        result = log_filter.filter(record)
        
        assert result is True  # Always returns True
        assert record.args == ()  # Args cleared
        # Message should be protected
        assert "123-45-6789" not in str(record.msg)

    def test_filter_always_returns_true(self, log_filter: SecureAILogFilter) -> None:
        """Test that filter always allows logs through."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Normal message",
            args=(),
            exc_info=None,
        )
        
        result = log_filter.filter(record)
        assert result is True

    def test_filter_handles_errors_gracefully(self) -> None:
        """Test that filter doesn't break logging if it encounters errors."""
        # Create a detector that will raise an error
        detector_mock = Mock()
        detector_mock.detect.side_effect = Exception("Test error")
        
        log_filter = SecureAILogFilter(detector=detector_mock)
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        
        # Should not raise, should return True
        result = log_filter.filter(record)
        assert result is True

    def test_protect_message(self, log_filter: SecureAILogFilter) -> None:
        """Test message protection logic."""
        from secureai.detection.entities import PIIEntity
        
        entities = [
            PIIEntity(
                entity_type=EntityType.SSN,
                value="123-45-6789",
                start=12,
                end=23,
            )
        ]
        
        message = "User SSN is 123-45-6789 today"
        protected = log_filter._protect_message(message, entities)
        
        assert "123-45-6789" not in protected
        assert "User SSN is" in protected
        assert "today" in protected

    def test_get_strategy_for_entity_with_policy(self) -> None:
        """Test getting strategy from policy."""
        policy = Policy(
            policy_id="test",
            name="Test",
            rules=[
                MaskingRule(
                    entity_type=EntityType.EMAIL,
                    strategy=MaskingStrategy.FULL_MASK,
                    contexts=["logs"],
                )
            ],
        )
        
        with patch.object(PolicyManager, "_fetch_policy"):
            policy_manager = PolicyManager(
                api_key="test", sync_interval=0, fallback_policy=policy
            )
            policy_manager._policy = policy
        
        log_filter = SecureAILogFilter(policy_manager=policy_manager)
        strategy = log_filter._get_strategy_for_entity(EntityType.EMAIL)
        
        assert strategy == MaskingStrategy.FULL_MASK

    def test_get_strategy_for_entity_default(self, log_filter: SecureAILogFilter) -> None:
        """Test getting default strategy when no policy."""
        strategy = log_filter._get_strategy_for_entity(EntityType.SSN)
        assert strategy == MaskingStrategy.PARTIAL_MASK

    def test_get_strategy_for_api_key(self, log_filter: SecureAILogFilter) -> None:
        """Test that API keys are fully masked by default."""
        strategy = log_filter._get_strategy_for_entity(EntityType.API_KEY)
        assert strategy == MaskingStrategy.FULL_MASK

    def test_get_strategy_for_password(self, log_filter: SecureAILogFilter) -> None:
        """Test that passwords are redacted by default."""
        strategy = log_filter._get_strategy_for_entity(EntityType.PASSWORD)
        assert strategy == MaskingStrategy.REDACT


class TestInstallLogProtection:
    """Test suite for install_log_protection function."""

    def test_install_on_root_logger(self) -> None:
        """Test installing protection on root logger."""
        # Clear any existing filters
        root_logger = logging.getLogger()
        root_logger.filters.clear()
        
        filter_instance = install_log_protection()
        
        assert filter_instance is not None
        assert isinstance(filter_instance, SecureAILogFilter)
        assert filter_instance in root_logger.filters

    def test_install_on_specific_logger(self) -> None:
        """Test installing protection on specific logger."""
        logger = logging.getLogger("specific_logger")
        logger.filters.clear()
        
        filter_instance = install_log_protection(logger=logger)
        
        assert filter_instance in logger.filters

    def test_install_with_policy_manager(self) -> None:
        """Test installing with policy manager."""
        policy = Policy(policy_id="test", name="Test", rules=[])
        
        with patch.object(PolicyManager, "_fetch_policy"):
            policy_manager = PolicyManager(
                api_key="test", sync_interval=0, fallback_policy=policy
            )
        
        logger = logging.getLogger("test_install")
        logger.filters.clear()
        
        filter_instance = install_log_protection(
            policy_manager=policy_manager, logger=logger
        )
        
        assert filter_instance.policy_manager is policy_manager


class TestLoggingIntegration:
    """Integration tests for logging protection."""

    def test_full_logging_workflow(self) -> None:
        """Test complete logging workflow with protection."""
        # Create a logger with string handler
        logger = logging.getLogger("integration_test")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.filters.clear()
        
        string_io = StringIO()
        handler = logging.StreamHandler(string_io)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)
        
        # Install protection
        install_log_protection(logger=logger)
        
        # Log messages with PII
        logger.info("Processing user with SSN 123-45-6789")
        logger.warning("Failed login for john@example.com")
        logger.error("Credit card 4532-1234-5678-9010 declined")
        
        output = string_io.getvalue()
        
        # Original PII should not be in output
        assert "123-45-6789" not in output
        assert "john@example.com" not in output
        assert "4532-1234-5678-9010" not in output
        
        # Log levels should still be there
        assert "INFO:" in output
        assert "WARNING:" in output
        assert "ERROR:" in output
        
        # Some masking should have occurred
        assert "*" in output or "REDACTED" in output

    def test_logging_with_formatting(self) -> None:
        """Test logging with string formatting."""
        logger = logging.getLogger("format_test")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.filters.clear()
        
        string_io = StringIO()
        handler = logging.StreamHandler(string_io)
        logger.addHandler(handler)
        
        install_log_protection(logger=logger)
        
        ssn = "123-45-6789"
        logger.info(f"User SSN: {ssn}")
        
        output = string_io.getvalue()
        assert "123-45-6789" not in output

    def test_logging_performance(self) -> None:
        """Test that logging protection doesn't significantly impact performance."""
        import time
        
        logger = logging.getLogger("perf_test")
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.filters.clear()
        
        # Use a null handler for performance testing
        logger.addHandler(logging.NullHandler())
        install_log_protection(logger=logger)
        
        # Log many messages
        start = time.time()
        for i in range(100):
            logger.info(f"Log message {i} with no PII")
        elapsed = time.time() - start
        
        # Should complete quickly (< 1 second for 100 logs)
        assert elapsed < 1.0


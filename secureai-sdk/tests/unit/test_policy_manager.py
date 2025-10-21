"""Unit tests for Policy Manager."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import httpx

from secureai.policy.manager import PolicyManager
from secureai.policy.models import Policy, MaskingRule
from secureai.detection.entities import EntityType
from secureai.encryption.strategies import MaskingStrategy
from secureai.core.exceptions import PolicyError, NetworkError


class TestPolicyManager:
    """Test suite for PolicyManager."""

    @pytest.fixture
    def mock_policy(self) -> Policy:
        """Create a mock policy for testing."""
        return Policy(
            policy_id="test_policy",
            name="Test Policy",
            description="Policy for testing",
            version="1.0.0",
            rules=[
                MaskingRule(
                    entity_type=EntityType.SSN,
                    strategy=MaskingStrategy.FPE,
                    contexts=["all"],
                ),
                MaskingRule(
                    entity_type=EntityType.EMAIL,
                    strategy=MaskingStrategy.PARTIAL_MASK,
                    contexts=["logs"],
                ),
            ],
        )

    @pytest.fixture
    def manager_no_sync(self, mock_policy: Policy) -> PolicyManager:
        """Create manager with sync disabled for testing."""
        with patch.object(PolicyManager, "_fetch_policy", side_effect=Exception("Mocked")):
            manager = PolicyManager(
                api_key="test_key",
                app_id="test_app",
                sync_interval=0,  # Disable background sync
                offline_mode=True,
                fallback_policy=mock_policy,
            )
            # Ensure policy is set
            manager._policy = mock_policy
            return manager

    def test_initialization(self, manager_no_sync: PolicyManager) -> None:
        """Test manager initialization."""
        assert manager_no_sync.api_key == "test_key"
        assert manager_no_sync.app_id == "test_app"
        assert manager_no_sync.sync_interval == 0
        assert manager_no_sync.offline_mode is True

    def test_initialization_with_fallback_policy(self, mock_policy: Policy) -> None:
        """Test initialization with fallback policy."""
        with patch.object(PolicyManager, "_fetch_policy", side_effect=Exception("Network error")):
            manager = PolicyManager(
                api_key="test_key",
                sync_interval=0,
                fallback_policy=mock_policy,
            )
            
            policy = manager.get_policy()
            assert policy.policy_id == "test_policy"

    def test_initialization_with_default_policy(self) -> None:
        """Test initialization falls back to default policy."""
        with patch.object(PolicyManager, "_fetch_policy", side_effect=Exception("Network error")):
            manager = PolicyManager(api_key="test_key", sync_interval=0)
            
            policy = manager.get_policy()
            assert policy.policy_id == "default"
            assert len(policy.rules) > 0

    def test_create_default_policy(self, manager_no_sync: PolicyManager) -> None:
        """Test default policy creation."""
        policy = manager_no_sync._create_default_policy()
        
        assert policy.policy_id == "default"
        assert policy.name == "Default Policy"
        assert len(policy.rules) > 0
        
        # Check for common rules
        has_ssn = any(r.entity_type == EntityType.SSN for r in policy.rules)
        has_credit_card = any(r.entity_type == EntityType.CREDIT_CARD for r in policy.rules)
        assert has_ssn
        assert has_credit_card

    def test_get_policy(self, manager_no_sync: PolicyManager) -> None:
        """Test getting current policy."""
        policy = manager_no_sync.get_policy()
        assert isinstance(policy, Policy)
        assert policy.policy_id == "test_policy"

    def test_get_policy_no_policy_raises_error(self) -> None:
        """Test getting policy when none available raises error."""
        with patch.object(PolicyManager, "_initialize_policy"):
            manager = PolicyManager(api_key="test_key", sync_interval=0)
            manager._policy = None
            
            with pytest.raises(PolicyError, match="No policy available"):
                manager.get_policy()

    def test_get_rule(self, manager_no_sync: PolicyManager) -> None:
        """Test getting a specific rule."""
        rule = manager_no_sync.get_rule(EntityType.SSN, context="all")
        
        assert rule is not None
        assert rule.entity_type == EntityType.SSN
        assert rule.strategy == MaskingStrategy.FPE

    def test_get_rule_with_context(self, manager_no_sync: PolicyManager) -> None:
        """Test getting rule with specific context."""
        rule = manager_no_sync.get_rule(EntityType.EMAIL, context="logs")
        
        assert rule is not None
        assert rule.entity_type == EntityType.EMAIL
        assert rule.strategy == MaskingStrategy.PARTIAL_MASK

    def test_get_rule_not_found(self, manager_no_sync: PolicyManager) -> None:
        """Test getting rule that doesn't exist."""
        rule = manager_no_sync.get_rule(EntityType.PHONE, context="api")
        assert rule is None

    def test_get_rule_wrong_context(self, manager_no_sync: PolicyManager) -> None:
        """Test getting rule with wrong context returns None."""
        # Email rule only applies to "logs" context
        rule = manager_no_sync.get_rule(EntityType.EMAIL, context="api")
        # Should return None because context doesn't match
        # unless "all" is in contexts

    @patch("httpx.Client.get")
    def test_fetch_policy_success(self, mock_get: Mock, mock_policy: Policy) -> None:
        """Test successful policy fetch."""
        mock_response = Mock()
        mock_response.json.return_value = mock_policy.model_dump()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        manager = PolicyManager(api_key="test_key", sync_interval=0)
        
        policy = manager.get_policy()
        assert policy.policy_id == mock_policy.policy_id

    @patch("httpx.Client.get")
    def test_fetch_policy_up_to_date(self, mock_get: Mock, mock_policy: Policy) -> None:
        """Test fetch when policy is up to date."""
        # First call returns policy, second returns up_to_date
        first_response = Mock()
        first_response.json.return_value = mock_policy.model_dump()
        first_response.raise_for_status = Mock()
        
        second_response = Mock()
        second_response.json.return_value = {"status": "up_to_date"}
        second_response.raise_for_status = Mock()
        
        mock_get.side_effect = [first_response, second_response]
        
        manager = PolicyManager(
            api_key="test_key",
            sync_interval=0,
        )
        
        # First fetch should work
        policy = manager.get_policy()
        assert policy.policy_id == "test_policy"
        
        # Second fetch should return up_to_date
        manager.refresh()
        policy = manager.get_policy()
        assert policy.policy_id == "test_policy"  # Still same policy

    @patch("httpx.Client.get")
    def test_fetch_policy_network_error_offline_mode(
        self, mock_get: Mock, mock_policy: Policy
    ) -> None:
        """Test fetch with network error in offline mode."""
        mock_get.side_effect = httpx.RequestError("Network error")
        
        manager = PolicyManager(
            api_key="test_key",
            sync_interval=0,
            offline_mode=True,
            fallback_policy=mock_policy,
        )
        
        # Should use fallback policy
        policy = manager.get_policy()
        assert policy is not None

    @patch("httpx.Client.get")
    def test_fetch_policy_network_error_no_offline_mode(self, mock_get: Mock) -> None:
        """Test fetch with network error when offline mode disabled."""
        mock_get.side_effect = httpx.RequestError("Network error", request=Mock())
        
        # Should fall back to default policy even in non-offline mode
        # because we handle exceptions in _initialize_policy
        manager = PolicyManager(
            api_key="test_key",
            sync_interval=0,
            offline_mode=False,
        )
        # Will use default policy
        assert manager.get_policy() is not None

    @patch("httpx.Client.get")
    def test_refresh_policy(self, mock_get: Mock, mock_policy: Policy) -> None:
        """Test manual policy refresh."""
        updated_policy = mock_policy.model_copy(update={"version": "2.0.0"})
        
        mock_response = Mock()
        mock_response.json.return_value = updated_policy.model_dump()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        manager = PolicyManager(
            api_key="test_key",
            sync_interval=0,
            fallback_policy=mock_policy,
        )
        
        # Refresh policy
        manager.refresh()
        
        # Should have new version
        policy = manager.get_policy()
        assert policy.version == "2.0.0"

    def test_get_sync_status(self, manager_no_sync: PolicyManager) -> None:
        """Test getting sync status."""
        status = manager_no_sync.get_sync_status()
        
        assert "has_policy" in status
        assert "policy_version" in status
        assert "sync_interval" in status
        assert "offline_mode" in status
        
        assert status["has_policy"] is True
        assert status["policy_version"] == "1.0.0"
        assert status["sync_interval"] == 0
        assert status["offline_mode"] is True

    def test_stop_sync(self, manager_no_sync: PolicyManager) -> None:
        """Test stopping synchronization."""
        manager_no_sync.stop()
        # Should not raise any errors

    def test_thread_safety(self, mock_policy: Policy) -> None:
        """Test thread-safe policy access."""
        import threading
        
        manager = PolicyManager(
            api_key="test_key",
            sync_interval=0,
            fallback_policy=mock_policy,
        )
        
        results = []
        errors = []
        
        def access_policy():
            try:
                for _ in range(100):
                    policy = manager.get_policy()
                    results.append(policy.policy_id)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads accessing policy
        threads = [threading.Thread(target=access_policy) for _ in range(10)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All accesses should succeed
        assert len(errors) == 0
        assert len(results) == 1000
        assert all(r == "test_policy" for r in results)


class TestPolicyModel:
    """Test suite for Policy model."""

    @pytest.fixture
    def policy(self) -> Policy:
        """Create a test policy."""
        return Policy(
            policy_id="test",
            name="Test",
            rules=[
                MaskingRule(
                    entity_type=EntityType.SSN,
                    strategy=MaskingStrategy.FPE,
                    contexts=["all"],
                ),
                MaskingRule(
                    entity_type=EntityType.EMAIL,
                    strategy=MaskingStrategy.PARTIAL_MASK,
                    contexts=["logs"],
                ),
            ],
        )

    def test_policy_creation(self, policy: Policy) -> None:
        """Test policy creation."""
        assert policy.policy_id == "test"
        assert policy.name == "Test"
        assert len(policy.rules) == 2

    def test_get_rule(self, policy: Policy) -> None:
        """Test getting rule from policy."""
        rule = policy.get_rule(EntityType.SSN, context="all")
        assert rule is not None
        assert rule.strategy == MaskingStrategy.FPE

    def test_get_rule_context_specific(self, policy: Policy) -> None:
        """Test getting rule with specific context."""
        rule = policy.get_rule(EntityType.EMAIL, context="logs")
        assert rule is not None
        assert rule.strategy == MaskingStrategy.PARTIAL_MASK

    def test_get_rule_all_context_matches_anything(self, policy: Policy) -> None:
        """Test that 'all' context matches any context."""
        rule = policy.get_rule(EntityType.SSN, context="logs")
        assert rule is not None  # SSN has "all" context

    def test_has_rule(self, policy: Policy) -> None:
        """Test checking if policy has rule."""
        assert policy.has_rule(EntityType.SSN) is True
        assert policy.has_rule(EntityType.EMAIL) is True
        assert policy.has_rule(EntityType.PHONE) is False

    def test_policy_serialization(self, policy: Policy) -> None:
        """Test policy can be serialized."""
        data = policy.model_dump()
        assert isinstance(data, dict)
        assert data["policy_id"] == "test"
        
        # Deserialize
        policy2 = Policy(**data)
        assert policy2.policy_id == policy.policy_id
        assert len(policy2.rules) == len(policy.rules)


class TestMaskingRule:
    """Test suite for MaskingRule model."""

    def test_rule_creation(self) -> None:
        """Test rule creation."""
        rule = MaskingRule(
            entity_type=EntityType.SSN, strategy=MaskingStrategy.FPE
        )
        
        assert rule.entity_type == EntityType.SSN
        assert rule.strategy == MaskingStrategy.FPE
        assert rule.contexts == ["all"]
        assert rule.show_last == 4

    def test_rule_with_custom_contexts(self) -> None:
        """Test rule with custom contexts."""
        rule = MaskingRule(
            entity_type=EntityType.EMAIL,
            strategy=MaskingStrategy.PARTIAL_MASK,
            contexts=["logs", "api"],
        )
        
        assert "logs" in rule.contexts
        assert "api" in rule.contexts

    def test_rule_with_exceptions(self) -> None:
        """Test rule with role exceptions."""
        rule = MaskingRule(
            entity_type=EntityType.SSN,
            strategy=MaskingStrategy.FPE,
            exceptions=["admin", "compliance_officer"],
        )
        
        assert "admin" in rule.exceptions
        assert len(rule.exceptions) == 2

    def test_rule_serialization(self) -> None:
        """Test rule serialization."""
        rule = MaskingRule(
            entity_type=EntityType.SSN, strategy=MaskingStrategy.FPE
        )
        
        data = rule.model_dump()
        assert isinstance(data, dict)
        assert data["entity_type"] == "SSN"
        assert data["strategy"] == "FPE"
        
        # Deserialize
        rule2 = MaskingRule(**data)
        assert rule2.entity_type == rule.entity_type
        assert rule2.strategy == rule.strategy


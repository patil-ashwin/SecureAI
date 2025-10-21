"""
Policy Manager.

Manages policy synchronization from central platform, caching, and offline mode.
"""

import threading
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

import httpx

from secureai.policy.models import Policy, MaskingRule
from secureai.detection.entities import EntityType
from secureai.encryption.strategies import MaskingStrategy
from secureai.core.exceptions import PolicyError, NetworkError

logger = logging.getLogger(__name__)


class PolicyManager:
    """
    Manages policies with background sync from central platform.
    
    Features:
    - Background policy synchronization
    - Local caching for performance
    - Offline mode with cached policies
    - Thread-safe operations
    
    Examples:
        >>> manager = PolicyManager(
        ...     api_key="secai_key",
        ...     app_id="my-app",
        ...     sync_interval=300
        ... )
        >>> policy = manager.get_policy()
        >>> rule = manager.get_rule(EntityType.SSN, context="logs")
    """

    def __init__(
        self,
        api_key: str,
        app_id: str = "default",
        base_url: str = "https://api.secureai.com",
        sync_interval: int = 300,  # 5 minutes
        offline_mode: bool = True,
        fallback_policy: Optional[Policy] = None,
    ):
        """
        Initialize Policy Manager.
        
        Args:
            api_key: API key for central platform
            app_id: Application identifier
            base_url: Base URL for central platform API
            sync_interval: Seconds between policy syncs
            offline_mode: Use cached policy if platform unreachable
            fallback_policy: Fallback policy if no cache available
        """
        self.api_key = api_key
        self.app_id = app_id
        self.base_url = base_url.rstrip("/")
        self.sync_interval = sync_interval
        self.offline_mode = offline_mode
        self.fallback_policy = fallback_policy
        
        # Cached policy
        self._policy: Optional[Policy] = None
        self._policy_lock = threading.Lock()
        
        # Sync state
        self._last_sync: Optional[datetime] = None
        self._sync_thread: Optional[threading.Thread] = None
        self._stop_sync = threading.Event()
        
        # HTTP client
        self._client = httpx.Client(
            timeout=10.0,
            headers={
                "X-API-Key": self.api_key,
                "User-Agent": "SecureAI-Python-SDK/0.1.0",
            },
        )
        
        # Initialize with default or fallback policy
        self._initialize_policy()
        
        # Start background sync if interval > 0
        if self.sync_interval > 0:
            self._start_background_sync()

    def _initialize_policy(self) -> None:
        """Initialize with default policy or fetch from platform."""
        try:
            # Try to fetch from platform
            self._fetch_policy()
        except Exception as e:
            logger.warning(f"Initial policy fetch failed: {e}")
            
            # Use fallback policy if provided
            if self.fallback_policy:
                with self._policy_lock:
                    self._policy = self.fallback_policy
                logger.info("Using fallback policy")
            else:
                # Create default policy
                with self._policy_lock:
                    self._policy = self._create_default_policy()
                logger.info("Using default policy")

    def _create_default_policy(self) -> Policy:
        """Create a sensible default policy."""
        return Policy(
            policy_id="default",
            name="Default Policy",
            description="Default protection policy",
            version="1.0.0",
            rules=[
                MaskingRule(
                    entity_type=EntityType.SSN,
                    strategy=MaskingStrategy.FPE,
                    contexts=["all"],
                ),
                MaskingRule(
                    entity_type=EntityType.CREDIT_CARD,
                    strategy=MaskingStrategy.TOKENIZE,
                    contexts=["all"],
                ),
                MaskingRule(
                    entity_type=EntityType.EMAIL,
                    strategy=MaskingStrategy.PARTIAL_MASK,
                    contexts=["logs"],
                ),
                MaskingRule(
                    entity_type=EntityType.PHONE,
                    strategy=MaskingStrategy.PARTIAL_MASK,
                    contexts=["logs"],
                ),
                MaskingRule(
                    entity_type=EntityType.API_KEY,
                    strategy=MaskingStrategy.FULL_MASK,
                    contexts=["all"],
                ),
                MaskingRule(
                    entity_type=EntityType.PASSWORD,
                    strategy=MaskingStrategy.REDACT,
                    contexts=["all"],
                ),
            ],
        )

    def _start_background_sync(self) -> None:
        """Start background thread for policy synchronization."""
        self._sync_thread = threading.Thread(
            target=self._background_sync_loop, daemon=True, name="PolicySync"
        )
        self._sync_thread.start()
        logger.info(f"Background policy sync started (interval: {self.sync_interval}s)")

    def _background_sync_loop(self) -> None:
        """Background loop for syncing policies."""
        while not self._stop_sync.is_set():
            # Wait for sync interval
            if self._stop_sync.wait(timeout=self.sync_interval):
                break  # Stop event was set
            
            try:
                self._fetch_policy()
            except Exception as e:
                logger.error(f"Background policy sync failed: {e}")
                # Continue with cached policy if offline mode enabled

    def _fetch_policy(self) -> None:
        """Fetch policy from central platform."""
        try:
            url = f"{self.base_url}/api/v1/policies"
            params = {"app_id": self.app_id}
            
            # Include current version for conditional fetch
            with self._policy_lock:
                if self._policy:
                    params["current_version"] = self._policy.version
            
            response = self._client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if policy was updated
            if data.get("status") == "up_to_date":
                logger.debug("Policy is up to date")
                return
            
            # Parse and cache new policy
            policy = Policy(**data)
            
            with self._policy_lock:
                old_version = self._policy.version if self._policy else "none"
                self._policy = policy
                self._last_sync = datetime.now()
            
            logger.info(f"Policy updated: {old_version} -> {policy.version}")
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 304:
                logger.debug("Policy not modified (304)")
                return
            raise NetworkError(f"HTTP error fetching policy: {e}") from e
        except httpx.RequestError as e:
            if self.offline_mode and self._policy:
                logger.warning(f"Policy fetch failed, using cached: {e}")
                return
            raise NetworkError(f"Network error fetching policy: {e}") from e
        except Exception as e:
            raise PolicyError(f"Failed to parse policy: {e}") from e

    def get_policy(self) -> Policy:
        """
        Get current policy.
        
        Returns:
            Current policy
            
        Raises:
            PolicyError: If no policy available
        """
        with self._policy_lock:
            if self._policy is None:
                raise PolicyError("No policy available")
            return self._policy

    def get_rule(
        self, entity_type: EntityType, context: str = "all"
    ) -> Optional[MaskingRule]:
        """
        Get masking rule for specific entity type and context.
        
        Args:
            entity_type: Type of entity
            context: Context (e.g., "logs", "api", "llm")
        
        Returns:
            Matching rule or None
        """
        policy = self.get_policy()
        return policy.get_rule(entity_type, context)

    def refresh(self) -> None:
        """Force immediate policy refresh from platform."""
        logger.info("Forcing policy refresh")
        self._fetch_policy()

    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get synchronization status.
        
        Returns:
            Dictionary with sync status information
        """
        with self._policy_lock:
            return {
                "has_policy": self._policy is not None,
                "policy_version": self._policy.version if self._policy else None,
                "last_sync": self._last_sync.isoformat() if self._last_sync else None,
                "sync_interval": self.sync_interval,
                "offline_mode": self.offline_mode,
                "sync_thread_alive": self._sync_thread.is_alive()
                if self._sync_thread
                else False,
            }

    def stop(self) -> None:
        """Stop background sync and cleanup."""
        if self._sync_thread and self._sync_thread.is_alive():
            logger.info("Stopping background policy sync")
            self._stop_sync.set()
            self._sync_thread.join(timeout=5)
        
        self._client.close()

    def __del__(self) -> None:
        """Cleanup on deletion."""
        try:
            self.stop()
        except Exception:
            pass  # Ignore errors during cleanup


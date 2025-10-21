"""Policy data models."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from secureai.detection.entities import EntityType
from secureai.encryption.strategies import MaskingStrategy


class MaskingRule(BaseModel):
    """Rule for masking a specific entity type."""

    entity_type: EntityType = Field(..., description="Type of entity to mask")
    strategy: MaskingStrategy = Field(..., description="Masking strategy to use")
    contexts: List[str] = Field(
        default_factory=lambda: ["all"], description="Contexts where rule applies"
    )
    show_last: int = Field(default=4, description="Characters to show for partial masking")
    exceptions: List[str] = Field(
        default_factory=list, description="Roles/users exempt from this rule"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic config."""

        use_enum_values = True


class Policy(BaseModel):
    """Complete policy definition."""

    policy_id: str = Field(..., description="Unique policy identifier")
    name: str = Field(..., description="Human-readable policy name")
    description: Optional[str] = Field(None, description="Policy description")
    version: str = Field(default="1.0.0", description="Policy version")
    environment: str = Field(default="production", description="Target environment")
    
    rules: List[MaskingRule] = Field(default_factory=list, description="Masking rules")
    
    enabled: bool = Field(default=True, description="Whether policy is active")
    
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def get_rule(self, entity_type: EntityType, context: str = "all") -> Optional[MaskingRule]:
        """
        Get masking rule for specific entity type and context.
        
        Args:
            entity_type: Type of entity
            context: Context (e.g., "logs", "api", "llm")
        
        Returns:
            Matching rule or None
        """
        for rule in self.rules:
            if rule.entity_type == entity_type:
                if "all" in rule.contexts or context in rule.contexts:
                    return rule
        return None

    def has_rule(self, entity_type: EntityType) -> bool:
        """Check if policy has a rule for entity type."""
        return any(rule.entity_type == entity_type for rule in self.rules)

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


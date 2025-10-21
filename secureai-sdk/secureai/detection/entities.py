"""PII entity models and types."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Types of PII entities that can be detected."""

    # Personal identifiers
    SSN = "SSN"
    PASSPORT = "PASSPORT"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    NATIONAL_ID = "NATIONAL_ID"

    # Financial
    CREDIT_CARD = "CREDIT_CARD"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    IBAN = "IBAN"
    ROUTING_NUMBER = "ROUTING_NUMBER"

    # Contact information
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    URL = "URL"
    IP_ADDRESS = "IP_ADDRESS"
    MAC_ADDRESS = "MAC_ADDRESS"

    # Personal information
    PERSON = "PERSON"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    AGE = "AGE"

    # Location
    ADDRESS = "ADDRESS"
    CITY = "CITY"
    STATE = "STATE"
    ZIP_CODE = "ZIP_CODE"
    COUNTRY = "COUNTRY"
    COORDINATES = "COORDINATES"

    # Medical
    MEDICAL_RECORD_NUMBER = "MEDICAL_RECORD_NUMBER"
    HEALTH_INSURANCE_NUMBER = "HEALTH_INSURANCE_NUMBER"
    PRESCRIPTION = "PRESCRIPTION"
    DOCTOR_NAME = "DOCTOR_NAME"

    # Other
    ORGANIZATION = "ORGANIZATION"
    API_KEY = "API_KEY"
    PASSWORD = "PASSWORD"
    JWT_TOKEN = "JWT_TOKEN"
    CUSTOM = "CUSTOM"

    def __str__(self) -> str:
        return self.value


class PIIEntity(BaseModel):
    """Model for a detected PII entity."""

    entity_type: EntityType = Field(..., description="Type of PII entity")
    value: str = Field(..., description="The actual PII value detected")
    start: int = Field(..., description="Start position in text")
    end: int = Field(..., description="End position in text")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confidence score (0-1)"
    )
    context: Optional[str] = Field(
        default=None, description="Surrounding context for better decisions"
    )
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Pydantic config."""

        frozen = False
        use_enum_values = True

    def __repr__(self) -> str:
        return (
            f"PIIEntity(type={self.entity_type}, value='{self.value}', "
            f"pos={self.start}-{self.end}, confidence={self.confidence:.2f})"
        )


class DetectionResult(BaseModel):
    """Result of PII detection on text."""

    text: str = Field(..., description="Original text")
    entities: list[PIIEntity] = Field(
        default_factory=list, description="Detected PII entities"
    )
    entity_count: int = Field(default=0, description="Total number of entities found")

    def model_post_init(self, __context) -> None:
        """Post-initialization to set entity count."""
        self.entity_count = len(self.entities)

    def get_entities_by_type(self, entity_type: EntityType) -> list[PIIEntity]:
        """Get all entities of a specific type."""
        return [e for e in self.entities if e.entity_type == entity_type]

    def has_entity_type(self, entity_type: EntityType) -> bool:
        """Check if a specific entity type was detected."""
        return any(e.entity_type == entity_type for e in self.entities)

    def get_unique_values(self, entity_type: Optional[EntityType] = None) -> set[str]:
        """Get unique values, optionally filtered by type."""
        if entity_type:
            return {e.value for e in self.entities if e.entity_type == entity_type}
        return {e.value for e in self.entities}


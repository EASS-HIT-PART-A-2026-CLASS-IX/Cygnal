from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, model_validator
from sqlmodel import Field, SQLModel

from backend.models.enums import IndicatorType, Severity
from backend.services.ioc_validation import validate_ioc_value


class IndicatorCreate(SQLModel):
    indicator_type: IndicatorType
    value: str
    severity: Severity
    source: str
    confidence: int = Field(ge=0, le=100)
    tags: List[str] = Field(default_factory=list)
    threat_actor: Optional[str] = None
    is_active: bool = True
    model_config = ConfigDict(extra="forbid")

    @field_validator("value", "source")
    @classmethod
    def reject_blank_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @model_validator(mode="after")
    def validate_typed_value(self):
        self.value = validate_ioc_value(self.indicator_type, self.value)
        return self


class IndicatorUpdate(SQLModel):
    severity: Optional[Severity] = None
    source: Optional[str] = None
    confidence: Optional[int] = Field(default=None, ge=0, le=100)
    tags: Optional[List[str]] = None
    threat_actor: Optional[str] = None
    is_active: Optional[bool] = None
    model_config = ConfigDict(extra="forbid")

    @field_validator("source")
    @classmethod
    def reject_blank_source(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class IndicatorRead(BaseModel):
    id: int
    indicator_type: IndicatorType
    value: str
    severity: Severity
    source: str
    confidence: int
    tags: List[str]
    threat_actor: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat().replace("+00:00", "Z")


class IndicatorPage(BaseModel):
    page: int
    page_size: int
    total: int
    items: List[IndicatorRead]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "page_size": 20,
                "total": 1,
                "items": [
                    {
                        "id": 1,
                        "indicator_type": "IP",
                        "value": "203.0.113.42",
                        "severity": "high",
                        "source": "analyst",
                        "confidence": 85,
                        "tags": ["scanning"],
                        "threat_actor": None,
                        "is_active": True,
                        "created_at": "2026-06-21T12:00:00Z",
                    }
                ],
            }
        }
    )

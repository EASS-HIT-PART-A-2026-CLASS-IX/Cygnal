from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum
from datetime import datetime, timezone

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IndicatorType(str, Enum):
    IP = "IP"
    DOMAIN = "Domain"
    URL = "URL"
    HASH = "Hash"
    EMAIL = "Email"

class IndicatorBase(BaseModel):
    """שדות משותפים לכל המודלים."""
    indicator_type: IndicatorType = Field(..., description="סוג האיום")
    value: str = Field(..., description="הערך עצמו, למשל 1.1.1.1")
    severity: SeverityLevel = Field(default=SeverityLevel.MEDIUM)
    source: str = Field(..., description="מאיפה הגיע המידע")
    confidence: int = Field(default=50, ge=0, le=100, description="רמת ביטחון 0-100")
    tags: List[str] = Field(default_factory=list, description="תיוגים חופשיים")
    threat_actor: Optional[str] = Field(default=None, description="הגורם מאחורי האיום")
    is_active: bool = Field(default=True)

class IndicatorCreate(IndicatorBase):
    """מודל לקבלת payload ביצירת indicator חדש עם ולידציה."""
    
    @field_validator("value")
    @classmethod
    def normalize_value(cls, v: str) -> str:
        """Strip whitespace from value."""
        return v.strip()

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, v: List[str]) -> List[str]:
        """Convert all tags to lowercase and strip whitespace."""
        return [tag.strip().lower() for tag in v]

class ThreatIndicator(IndicatorBase):
    """מודל תגובה – כולל ID ותאריכים שנוצרים בשרת."""
    id: Optional[int] = None
    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "indicator_type": "IP",
                "value": "192.168.1.1",
                "severity": "high",
                "source": "AbuseIPDB",
                "confidence": 85,
                "tags": ["ransomware", "apt29"],
                "threat_actor": "Lazarus Group",
                "is_active": True
            }
        }
    }
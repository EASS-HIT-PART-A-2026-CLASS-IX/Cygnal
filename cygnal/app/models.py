from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

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

class ThreatIndicator(BaseModel):
    id: Optional[int] = None
    indicator_type: IndicatorType = Field(..., description="The category of the threat")
    value: str = Field(..., description="The actual indicator value (e.g., 1.1.1.1)")
    severity: SeverityLevel = Field(default=SeverityLevel.MEDIUM, description="Severity of the threat")
    source: str = Field(..., description="The origin of the intelligence data")

    # דוגמה לערכים שיופיעו ב-Swagger
    model_config = {
        "json_schema_extra": {
            "example": {
                "indicator_type": "IP",
                "value": "192.168.1.1",
                "severity": "high",
                "source": "Sentinel-Internal"
            }
        }
    }
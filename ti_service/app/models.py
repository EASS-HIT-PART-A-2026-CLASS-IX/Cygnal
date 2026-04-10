from pydantic import BaseModel, Field
from typing import Optional

class ThreatIndicator(BaseModel):
    id: Optional[int] = None
    indicator_type: str = Field(..., description="e.g., IP, Domain, URL, Hash")
    value: str = Field(..., description="The actual indicator value")
    severity: str = Field(default="medium", description="low, medium, high, critical")
    source: str = Field(..., description="Where the intel came from")
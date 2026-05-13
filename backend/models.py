from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, JSON

class IndicatorBase(SQLModel):
    indicator_type: str = Field(index=True)
    value: str
    severity: str
    source: str
    confidence: int = Field(ge=0, le=100)
    # בגלל ש-SQLite לא תומך ברשימות רגילות, אנחנו אומרים לו לשמור את זה כ-JSON
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    threat_actor: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Indicator(IndicatorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class IndicatorCreate(IndicatorBase):
    pass

class IndicatorUpdate(SQLModel):
    severity: Optional[str] = None
    confidence: Optional[int] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None
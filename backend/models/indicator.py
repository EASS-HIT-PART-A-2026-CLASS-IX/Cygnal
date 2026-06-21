from datetime import datetime, timezone
from typing import List, Optional

from pydantic import field_serializer
from sqlalchemy import Enum as SAEnum
from sqlmodel import JSON, Column, Field, SQLModel

from backend.models.enums import IndicatorType, Severity


class Indicator(SQLModel, table=True):  # type: ignore[call-arg]
    id: Optional[int] = Field(default=None, primary_key=True)
    indicator_type: IndicatorType = Field(
        sa_column=Column(
            SAEnum(IndicatorType, values_callable=lambda members: [member.value for member in members]), index=True
        )
    )
    value: str
    severity: Severity = Field(
        sa_column=Column(SAEnum(Severity, values_callable=lambda members: [member.value for member in members]))
    )
    source: str
    confidence: int = Field(ge=0, le=100)
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    threat_actor: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat().replace("+00:00", "Z")

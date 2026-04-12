from typing import Dict, List, Optional
from .models import ThreatIndicator, IndicatorCreate


class ThreatRepository:

    def __init__(self):
        self._indicators: Dict[int, ThreatIndicator] = {}
        self._next_id = 1

    def list(self) -> List[ThreatIndicator]:
        return list(self._indicators.values())

    def create(self, payload: IndicatorCreate) -> ThreatIndicator:
        indicator = ThreatIndicator(id=self._next_id, **payload.model_dump())
        self._indicators[self._next_id] = indicator
        self._next_id += 1
        return indicator

    def get(self, indicator_id: int) -> Optional[ThreatIndicator]:
        return self._indicators.get(indicator_id)

    def delete(self, indicator_id: int) -> bool:
        if indicator_id in self._indicators:
            del self._indicators[indicator_id]
            return True
        return False

    def clear(self) -> None:
        self._indicators.clear()
        self._next_id = 1


repo = ThreatRepository()
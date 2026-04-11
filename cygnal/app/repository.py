from typing import Dict, List, Optional
from .models import ThreatIndicator

class ThreatRepository:
    def __init__(self):
        # אחסון בזיכרון (In-memory) - יוחלף ב-SQLite ב-EX3
        self._indicators: Dict[int, ThreatIndicator] = {}
        self._next_id = 1

    def list(self) -> List[ThreatIndicator]:
        """מחזיר את כל האינדיקטורים הקיימים."""
        return list(self._indicators.values())

    def create(self, payload: ThreatIndicator) -> ThreatIndicator:
        """יוצר אינדיקטור חדש ומקצה לו ID."""
        payload.id = self._next_id
        self._indicators[self._next_id] = payload
        self._next_id += 1
        return payload

    def get(self, indicator_id: int) -> Optional[ThreatIndicator]:
        """שולף אינדיקטור ספציפי לפי ה-ID שלו."""
        return self._indicators.get(indicator_id)

    def delete(self, indicator_id: int) -> bool:
        """מוחק אינדיקטור ומחזיר True אם המחיקה הצליחה."""
        if indicator_id in self._indicators:
            del self._indicators[indicator_id]
            return True
        return False

# יצירת סינגלטון (Singleton) של ה-Repository לשימוש בכל האפליקציה
repo = ThreatRepository()
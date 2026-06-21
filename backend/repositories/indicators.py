from typing import List, Optional

from sqlmodel import Session, func, select

from backend.models.indicator import Indicator
from backend.schemas.indicators import IndicatorCreate, IndicatorType, IndicatorUpdate, Severity


class IndicatorRepository:
    @staticmethod
    def _apply_filters(statement, indicator_type, severity, is_active):
        if indicator_type is not None:
            statement = statement.where(Indicator.indicator_type == indicator_type)
        if severity is not None:
            statement = statement.where(Indicator.severity == severity)
        if is_active is not None:
            statement = statement.where(Indicator.is_active == is_active)
        return statement

    def get_all(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        indicator_type: IndicatorType | None = None,
        severity: Severity | None = None,
        is_active: bool | None = None,
    ) -> List[Indicator]:
        statement = self._apply_filters(select(Indicator), indicator_type, severity, is_active)
        return list(session.exec(statement.order_by(Indicator.id).offset(skip).limit(limit)).all())

    def count(
        self,
        session: Session,
        indicator_type: IndicatorType | None = None,
        severity: Severity | None = None,
        is_active: bool | None = None,
    ) -> int:
        statement = self._apply_filters(
            select(func.count()).select_from(Indicator), indicator_type, severity, is_active
        )
        return session.exec(statement).one()

    def get_by_id(self, session: Session, indicator_id: int) -> Optional[Indicator]:
        return session.get(Indicator, indicator_id)

    def create(self, session: Session, indicator_in: IndicatorCreate) -> Indicator:
        db_indicator = Indicator.model_validate(indicator_in)
        session.add(db_indicator)
        session.commit()
        session.refresh(db_indicator)
        return db_indicator

    def update(self, session: Session, indicator_id: int, update_data: IndicatorUpdate) -> Optional[Indicator]:
        db_indicator = session.get(Indicator, indicator_id)
        if not db_indicator:
            return None
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(db_indicator, field, value)
        session.add(db_indicator)
        session.commit()
        session.refresh(db_indicator)
        return db_indicator

    def delete(self, session: Session, indicator_id: int) -> bool:
        db_indicator = session.get(Indicator, indicator_id)
        if not db_indicator:
            return False
        session.delete(db_indicator)
        session.commit()
        return True


repo = IndicatorRepository()

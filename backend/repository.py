from typing import List, Optional

from sqlmodel import Session, select

from backend.models import Indicator, IndicatorCreate, IndicatorUpdate


class IndicatorRepository:

    def get_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[Indicator]:
        statement = select(Indicator).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    def get_by_id(self, session: Session, indicator_id: int) -> Optional[Indicator]:
        return session.get(Indicator, indicator_id)

    def create(self, session: Session, indicator_in: IndicatorCreate) -> Indicator:
        db_indicator = Indicator.model_validate(indicator_in)
        session.add(db_indicator)
        session.commit()
        session.refresh(db_indicator)
        return db_indicator

    def update(
        self, session: Session, indicator_id: int, update_data: IndicatorUpdate
    ) -> Optional[Indicator]:
        db_indicator = session.get(Indicator, indicator_id)
        if not db_indicator:
            return None
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
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
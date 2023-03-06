from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.crud.base import CRUDBase
from app.db.base import (
    GradingScale,
)
from app.schemas import (
    GradingScaleCreate,
    GradingScaleUpdate,
)


class CRUDGradingScale(CRUDBase[GradingScale, GradingScaleCreate, GradingScaleUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[GradingScale]:
        return db.query(self.model).filter(self.model.name == name).first()

    def get_by_percentage(self, db: Session, *, lowest_percentage: int, highest_percentage: int) -> Optional[GradingScale]:
        return db.query(self.model).filter(or_(self.model.lowest_percentage == lowest_percentage, self.model.highest_percentage == highest_percentage)).first()


grading_scale = CRUDGradingScale(GradingScale)

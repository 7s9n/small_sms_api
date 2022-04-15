from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.base import Grade
from app.schemas import (
    GradeCreate,
    GradeUpdate,
)

class CRUDGrade(CRUDBase[Grade, GradeCreate, GradeUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Grade]:
        return db.query(self.model).filter(Grade.name == name).first()


grade = CRUDGrade(Grade)

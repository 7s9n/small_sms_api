from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.base import Subject
from app.schemas import (
    SubjectCreate,
    SubjectUpdate,
)

class CRUDGrade(CRUDBase[Subject, SubjectCreate, SubjectUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Subject]:
        return db.query(self.model).filter(self.model.name == name).first()


subject = CRUDGrade(Subject)

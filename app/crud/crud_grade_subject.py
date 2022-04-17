from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.base import GradeSubject
from app.schemas import (
    GradeSubjectCreate,
    GradeSubjectUpdate,
)


class CRUDGradeSubject(CRUDBase[GradeSubject, GradeSubjectCreate, GradeSubjectUpdate]):
    def get(self, db: Session, grade_id: int, subject_id: int) -> Optional[GradeSubject]:
        return db.query(self.model).filter(
            self.model.grade_id == grade_id,
            self.model.subject_id == subject_id
        ).first()

    def remove(self, db: Session, *, grade_id: int, subject_id: int) -> GradeSubject:
        obj = db.query(self.model).filter(
            self.model.grade_id == grade_id, self.model.subject_id == subject_id
        ).first()
        db.delete(obj)
        db.commit()
        return obj


grade_subject = CRUDGradeSubject(GradeSubject)

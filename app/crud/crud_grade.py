from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.base import (
    Grade,
    Subject,
    GradeSubject,
)
from app.schemas import (
    GradeCreate,
    GradeUpdate,
)


class CRUDGrade(CRUDBase[Grade, GradeCreate, GradeUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Grade]:
        return db.query(self.model).filter(Grade.name == name).first()

    def get_grade_assigned_or_not_assigned_subjects(self, db: Session, *, grade_id: int, assigned: bool = True) -> Optional[List[Subject]]:
        subquery = db.query(GradeSubject.subject_id).filter(
            GradeSubject.grade_id == grade_id
        ).subquery()
        if assigned:
            subjects = db.query(Subject).filter(Subject.id.in_(subquery)).all()
        else:
            subjects = db.query(Subject).filter(Subject.id.notin_(subquery)).all()
        return subjects


grade = CRUDGrade(Grade)

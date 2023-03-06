from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.base import (
    Grade,
    Subject,
    subject_grades
    # GradeSubject,
)
from app.schemas import (
    GradeCreate,
    GradeUpdate,
)


class CRUDGrade(CRUDBase[Grade, GradeCreate, GradeUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Grade]:
        return db.query(self.model).filter(Grade.name == name).first()

    def get_by_name_and_level(self, db: Session, *, name: str, level_id: int) -> Optional[Grade]:
        return db.query(self.model).filter(Grade.name == name, Grade.level_id == level_id).first()

    def get_grade_assigned_or_not_assigned_subjects(self, db: Session, *, grade_id: int, assigned: bool = True) -> Optional[List[Subject]]:
        subquery = db.query(subject_grades.c.subject_id).filter(
            subject_grades.c.grade_id == grade_id
        ).subquery()
        if assigned:
            subjects = db.query(Subject).filter(Subject.id.in_(subquery)).all()
        else:
            subjects = db.query(Subject).filter(Subject.id.notin_(subquery)).all()
        return subjects


grade = CRUDGrade(Grade)

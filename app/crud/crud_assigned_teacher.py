from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.crud.base import CRUDBase
from app.db.base import AssignedTeacher
from app.schemas import (
    AssignedTeacherCreateInDB,
)

class CRUDAssignedTeacher(CRUDBase[AssignedTeacher, AssignedTeacherCreateInDB, AssignedTeacherCreateInDB]):
    def get_by_name(self, db: Session, name, **kwargs) -> Optional[AssignedTeacher]:
        return db.query(self.model).filter(self.model.name == name).first()
    def get(
        self, db: Session, grade_id: int, subject_id: int, school_year_id: int
    )-> AssignedTeacher | None:
        return db.query(self.model).filter(
            self.model.grade_id == grade_id,
            self.model.subject_id == subject_id,
            self.model.school_year_id == school_year_id
        ).first()
    def get_teacher_subjects(self, db: Session):
        pass
assigned_teacher = CRUDAssignedTeacher(AssignedTeacher)

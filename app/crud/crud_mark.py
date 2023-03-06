from typing import List, Optional
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func
from app.crud.base import CRUDBase
from app.db.base import (
    Mark,
    User,
    AssignedTeacher,
)
from app import models
from app.schemas import (
    MarkCreateInDB,
    MarkUpdate,
)


class CRUDMark(CRUDBase[Mark, MarkCreateInDB, MarkUpdate]):
    def has_permission_to_create_or_update_mark(
        self,
        db: Session, 
        teacher_id: int, 
        subject_id: int, 
        grade_id: int,
        school_year_id: int,
    )-> bool:
        return True if db.query(AssignedTeacher).filter(
            AssignedTeacher.subject_id == subject_id,
            AssignedTeacher.grade_id == grade_id,
            AssignedTeacher.teacher_id == teacher_id,
            AssignedTeacher.school_year_id == school_year_id,
        ).first() else False
    
    def get_joined_marks_query(self, db: Session):
        a1 = aliased(models.Mark, name="a1")
        query = db.query(
            models.User.id.label("student_id"),
            func.concat(models.User.first_name, " ", models.User.father_name, " ",
                        models.User.gfather_name, " ", models.User.last_name).label("student_name"),
            models.Grade.id.label("grade_id"),
            func.concat(models.Grade.name, " ",
                        models.Level.name).label("grade_name"),
            models.Subject.id.label("subject_id"),
            models.Subject.name.label("subject_name"),
            models.SchoolYear.id.label("school_year_id"),
            models.SchoolYear.title.label("school_year_title"),
            a1.month,
            a1.semaster,
            a1.attendance,
            a1.oral_test,
            a1.homeworks,
            a1.written_test,
            a1.school_year_id,
        ).select_from(a1).\
            join(
                models.User,
                models.User.id == a1.student_id,
        ).join(
                models.Grade,
                models.Grade.id == a1.grade_id,
        ).join(
                models.Level,
                models.Level.id == models.Grade.level_id,
        ).join(
                models.Subject,
                models.Subject.id == a1.subject_id,
        ).join(
            models.SchoolYear,
            models.SchoolYear.id == a1.school_year_id,
        )
        return query


mark = CRUDMark(Mark)
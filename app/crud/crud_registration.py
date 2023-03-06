from typing import (
    Optional,
    List,
    Dict,
    Any
)
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.base import (
    Registration,
    SchoolYear,
    Grade,
)
from app.schemas import (
    RegistrationCreate,
    RegistrationUpdate,
)


class CRUDRegistration(CRUDBase[Registration, RegistrationCreate, RegistrationUpdate]):
    def get_by_registration_no(self, db: Session, regi_no: str) -> Optional[Registration]:
        return db.query(self.model).filter(self.model.regi_no == regi_no).first()

    def get(self, db: Session, payload)-> Registration | None:
        return db.query(self.model).get(payload)
        
    def get_registration_by_grade_student_school_year(
        self,
        db: Session,
        student_id: Optional[int] = None,
        grade_id: Optional[int] = None,
        school_year_id: Optional[int] = None
    ):
        params = {"student_id": student_id, "grade_id": grade_id,
                  "school_year_id": school_year_id}
        query = db.query(self.model)
        for attr in [x for x in params if params[x] is not None]:
            query = query.filter(getattr(self.model, attr) == params[attr])

        return query.first()

    def generate_unique_regi_no(self, db: Session, school_year: SchoolYear, grade: Grade) -> str:
        regi_no = f"{getattr(school_year,'start_date').strftime('%y')}{getattr(school_year,'end_date').strftime('%y')}{getattr(grade,'numeric_value')}"
        total_students = db.query(Registration).filter(
            Registration.school_year_id == school_year.id,
            Registration.grade_id == grade.id
        ).count() + 1
        regi_no += str(total_students).rjust(3, '0')
        return regi_no


registeration = CRUDRegistration(Registration)

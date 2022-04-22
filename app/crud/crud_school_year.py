from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.base import SchoolYear
from app.schemas import (
    SchoolYearCreate,
    SchoolYearUpdate,
)


class CRUDSchoolYear(CRUDBase[SchoolYear, SchoolYearCreate, SchoolYearUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[SchoolYear]:
        return db.query(self.model).filter(self.model.title == name).first()

    def get_current_school_year(self, db: Session) -> Optional[SchoolYear]:
        return db.query(self.model).filter(self.model.is_active == True).first()

    def acivate_school_year(self, db: Session, school_year_id: int) -> SchoolYear:
        db.query(self.model).filter(
            self.model.is_active == True
        ).update({self.model.is_active: False}, synchronize_session=False)

        school_year_query = db.query(self.model).filter(
            self.model.id == school_year_id)
        school_year_query.update(
            {self.model.is_active: True}, synchronize_session=False)

        db.commit()
        return school_year_query.first()


school_year = CRUDSchoolYear(SchoolYear)

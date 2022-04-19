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


school_year = CRUDSchoolYear(SchoolYear)

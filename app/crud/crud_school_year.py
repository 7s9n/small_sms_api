from typing import (
    Optional,
    Dict,
    Any,
    List
)
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.crud.base import CRUDBase
from app.db.base import SchoolYear
from app.schemas import (
    SchoolYearCreate,
    SchoolYearUpdate,
)


class CRUDSchoolYear(CRUDBase[SchoolYear, SchoolYearCreate, SchoolYearUpdate]):
    # def get_multi(
    #     self, db: Session, *, page: int = 0, limit: int = 20, search: str = "", params: Dict[str, Any] = None
    # ) -> List[SchoolYear]:
    #     query = db.query(self.model)
    #     if params:
    #         for attr in [x for x in params if params[x] is not None]:
    #             query = query.filter(getattr(self.model, attr) == params[attr])
    #         query = query.filter(SchoolYear.title.like(f"%{search}%"))
    #     return query.order_by(desc(self.model.id)).offset((page - 1) * limit).limit(limit).all()

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
    
    def get_previous_school_year(self, db: Session)-> SchoolYear | None:
        last_two_school_years = db.query(self.model).order_by(desc(self.model.id)).limit(2).all()

        return None if len(last_two_school_years) < 2 else last_two_school_years[1]

school_year = CRUDSchoolYear(SchoolYear)

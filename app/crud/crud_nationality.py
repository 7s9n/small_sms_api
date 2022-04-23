from operator import or_
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.crud.base import CRUDBase
from app.db.base import Nationality
from app.schemas import (
    NationalityCreate,
    NationalityUpdate,
)


class CRUDNationality(CRUDBase[Nationality, NationalityCreate, NationalityUpdate]):
    def get_by_name(self, db: Session, name: str) -> Optional[Nationality]:
        return db.query(self.model).filter(
            or_(self.model.masculine_form == name,
                self.model.feminine_form == name)
        ).first()


nationality = CRUDNationality(Nationality)

from typing import Optional
from sqlalchemy.sql import or_ 
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.base import Subject
from app.schemas import (
    SubjectCreate,
    SubjectUpdate,
)

class CRUDSubject(CRUDBase[Subject, SubjectCreate, SubjectUpdate]):
    def get_by_name(self, db: Session, name, **kwargs) -> Optional[Subject]:
        #for searching
        # for k, v in kwargs.items(): 
        #     query = db.query(self.model).filter(getattr(self.model, k).like(f"%{v}%"))
        # return query.first()
        return db.query(self.model).filter(or_(self.model.name == name, self.model.foreign_name == name)).first()


subject = CRUDSubject(Subject)

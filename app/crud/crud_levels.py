from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.base import Level
from app.schemas import (
    LevelCreate,
    LevelUpdate,
)

class CRUDLevel(CRUDBase[Level, LevelCreate, LevelUpdate]):
    def get_by_name(self, db: Session, name, **kwargs) -> Optional[Level]:
        return db.query(self.model).filter(self.model.name == name).first()
level = CRUDLevel(Level)

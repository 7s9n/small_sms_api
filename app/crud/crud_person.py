from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.crud.base import CRUDBase
from app.models.person import Person
from app.schemas.person import PersonCreate, PersonUpdate

class CRUDPerson(CRUDBase[Person, PersonCreate, PersonUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[Person]:
        return db.query(self.model).filter(self.model.username == username).first()

    def is_active(self, person: Person) -> bool:
        return person.is_active

    def create(self, db: Session, *, obj_in: PersonCreate) -> Person:
        db_obj = self.model(
            username=obj_in.username,
            password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            father_name=obj_in.father_name,
            gfather_name=obj_in.gfather_name,
            last_name=obj_in.last_name,
            gender = obj_in.gender,
            date_of_birth = obj_in.date_of_birth,
            nationality_id = obj_in.nationality_id,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Person, obj_in: Union[PersonCreate, Dict[str, Any]]
    ) -> Person:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["password"]  = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)



person = CRUDPerson(Person)

from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.crud.base import CRUDBase
from app.models.teacher import Teacher
from app.schemas.user import AdminTeacherCreate, AdminTeacherUpdate

class CRUDTeacher(CRUDBase[Teacher, AdminTeacherCreate, AdminTeacherUpdate]):
    def create(self, db: Session, *, obj_in: AdminTeacherCreate) -> Teacher:
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
        self, db: Session, *, db_obj: Teacher, obj_in: Union[AdminTeacherCreate, Dict[str, Any]]
    ) -> Teacher:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["password"]  = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)



teacher = CRUDTeacher(Teacher)

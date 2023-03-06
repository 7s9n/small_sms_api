from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session, Query

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.registration import Registration
from app.schemas.user import UserCreate, UserUpdate, UserChangePassword
from sqlalchemy import func

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
    def create(self, db: Session, *, obj_in: UserCreate, role: str) -> User:
        db_obj = User(
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
            role=role
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def change_password(self, db: Session, db_obj: User, obj_in: UserChangePassword) -> User:

        db_obj.password = get_password_hash(obj_in.new_password)        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    def get_student(self, db: Session, id: int)-> User | None:
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.role == 's',
        ).first()
    def create_student(self, db: Session, *, obj_in: UserCreate)-> User:
        return self.create(db,obj_in=obj_in, role="s")

    def create_teacher(self, db: Session, *, obj_in: UserCreate)-> User:
        return self.create(db,obj_in=obj_in, role="t")

    def __get_all_users_by_role(self, db: Session, role: str)-> Query:
        return db.query(self.model).order_by(self.model.full_name).filter(self.model.role == role)

    def get_paginated_users(self, db: Session, page: int, limit: int, roles: list[str], search: str = None)-> tuple[list[User], int]:
        query = db.query(self.model).order_by(self.model.full_name).filter(self.model.role.in_(roles))
        if search:
            query = query.filter(self.model.full_name.like(f'%{search.strip()}%'))
        size = query.count()
        rows = query.offset((page - 1) * limit).limit(limit).all()
        return (rows, size)

    def get_all_teachers(self, db: Session)-> list[User]:
        return self.__get_all_users_by_role(db, role="t").all()

    def get_all_admins(self, db: Session)-> list[User]:
        return self.__get_all_users_by_role(db, role="a").all()

    def get_all_students(self, db: Session)-> list[User]:
        return self.__get_all_users_by_role(db, role="s").all()

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    def get_student_count_by_school_year_id(
            self,
            db:Session,
            school_year_id: int,
    ):
        return db.query(func.count(Registration.school_year_id))\
        .filter(
            Registration.school_year_id == school_year_id
        ).scalar()
    
    def get_male_student_count_by_school_year_id(
            self,
            db:Session,
            school_year_id: int,
    ):
        query = db.query(Registration.student_id)\
        .filter(
            Registration.school_year_id == school_year_id
        ).subquery(name="student_subquery")

        return db.query(self.model.id).filter(
            self.model.gender == True,
            self.model.id.in_(query)
        ).count()
    
    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.role == 'a'
    
    def is_teacher(self, user: User) -> bool:
        return user.role == 't'

    def is_student(self, user: User) -> bool:
        return user.role == 's'
    


user = CRUDUser(User)

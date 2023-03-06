from typing import Optional, List
from datetime import date
from datetime import datetime

from pydantic import (
    BaseModel,
    validator,
    constr,
    root_validator,
)
from app.schemas.nationality import NationalityInDB
from app.schemas import (
    SubjectInDB,
    GradeInDB
)
from app.schemas.pagination import Pagination


class UserBase(BaseModel):
    first_name: str
    father_name: str
    gfather_name: str
    last_name: str
    gender: bool
    date_of_birth: date
    nationality_id: int
    is_active: Optional[bool] = True
    username: str

    @validator("first_name")
    def validate_first_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('الاسم الأول يجب ألا يكون فارغًا.')
        return value

    @validator("father_name")
    def validate_father_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('لا يجب ترك اسم الأب فارغًا.')
        return value

    @validator("gfather_name")
    def validate_gfather_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('لا يجب ترك اسم الجد فارغًا.')
        return value

    @validator("last_name")
    def validate_last_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('الاسم الأخير يجب ألا يكون فارغًا.')
        return value

    @validator("date_of_birth", pre=True)
    def parse_date_of_birth(cls, value):
        if isinstance(value, date):
            return value
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    @validator("username")
    def validate_username(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('.إسم المستخدم يجب الأ يكون فارغاً')
        if len(value) < 2:
            raise ValueError("اسم المستخدم قصير جداً.")
        return value.lower()


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass

class UserChangePassword(BaseModel):
    old_password: str
    new_password: str

    @validator("new_password")
    def validate_password_length(cls, value: str):
        if len(value) < 6:
            raise ValueError("كلمة السر قصيرة جداً")
        return value

class AdminTeacherCreate(UserCreate):
    discriminator: constr(min_length=1, max_length=1,
                          strip_whitespace=True, regex=r"[A|T|a|t]")

    @validator("discriminator")
    def validate_discriminator(cls, value: str):
        return value.upper()


class AdminTeacherUpdate(UserBase):
    password: Optional[str] = None


class UserInDBase(UserBase):
    id: int
    role: str
    nationality: NationalityInDB
    full_name: Optional[str]

    @root_validator(pre=False)
    def full_name(cls, values):
        first_name, father_name, gfather_name, last_name = values.get('first_name', None), values.get('father_name', None), values.get('gfather_name', None), values.get('last_name', None)
        values["full_name"] = f'{first_name} {father_name} {gfather_name} {last_name}'
        return values

    class Config:
        orm_mode = True


class UserInDB(UserInDBase):
    hashed_password: str


class UserPaginatedResponse(BaseModel):
    data: List[UserInDBase]
    pagination: Pagination

class AssignedTeacherCreateRequest(BaseModel):
    teacher_id: int
    grade_id: int
    subject_id: int


class AssignedTeacherCreateInDB(AssignedTeacherCreateRequest):
    school_year_id: int

    class Config:
        orm_mode = True


class AssignedTeacherInDB(BaseModel):
    teacher: UserInDBase
    grade: GradeInDB
    subject: SubjectInDB

    class Config:
        orm_mode = True

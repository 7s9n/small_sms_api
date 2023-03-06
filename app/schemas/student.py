from typing import List
import re
from pydantic import (
    BaseModel,
    validator
)
from app.schemas.pagination import Pagination
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDBase,
    UserPaginatedResponse,
)
class StudentBase(UserBase):
    pass

class StudentCreate(UserCreate):
    pass


class StudentUpdate(UserUpdate):
    pass


class StudentInDB(UserInDBase):
    pass

    class Config:
        orm_mode = True

class StudentPaginatedResponse(UserPaginatedResponse):
    pass

class StudentRegistrations(BaseModel):
    grade_id: int
    grade_name: str
    school_year_id: int
    school_year_title: str

    class Config:
        orm_mode = True
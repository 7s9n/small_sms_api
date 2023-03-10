from typing import (
    List,
    Optional
)
from pydantic import (
    BaseModel,
    root_validator,
    validator
)
from .levels import LevelInDB
from .pagination import Pagination 
from .subject import SubjectInDB
from .utils import check_not_empty_str

class GradeBase(BaseModel):
    name: str
    numeric_value: int
    level_id: int
    notes: Optional[str] = None
    _name_not_empty = validator("name", allow_reuse=True)(check_not_empty_str("اسم الصف يجب ألا يكون فارغًا."))

class GradeCreate(GradeBase):
    pass


class GradeUpdate(GradeBase):
    pass


class GradeInDB(GradeBase):
    id: int
    level: LevelInDB
    composite_name: Optional[str]

    @root_validator(pre=False)
    def composite_grade_name(cls, values):
        name, level = values.get('name', None), values.get('level', None)
        values["composite_name"] = f'{name} {level.name}'
        return values

    class Config:
        orm_mode = True

class GradesResponseModel(BaseModel):
    data: List[GradeInDB]
    pagination: Pagination

class BasicGradeInfo(BaseModel):
    id: int
    composite_name: str

    class Config:
        orm_mode = True

# class BasicGradeInfo(BaseModel):
#     id: int
#     name: str
#     level: LevelInDB
#     composite_name: Optional[str]

#     @root_validator(pre=False)
#     def composite_grade_name(cls, values):
#         name, level = values.get('name', None), values.get('level', None)
#         values["composite_name"] = f'{name} {level.name}'
#         return values

#     class Config:
#         orm_mode = True
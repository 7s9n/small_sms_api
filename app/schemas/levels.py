from typing import List, Optional
from pydantic import BaseModel, validator
from .pagination import Pagination 
from .utils import check_not_empty_str
class LevelBase(BaseModel):
    name: str
    notes: Optional[str] = None

    _name_not_empty = validator("name", allow_reuse=True)(check_not_empty_str("اسم المرحلة يجب ألا يكون فارغًا."))
class LevelCreate(LevelBase):
    pass

class LevelUpdate(LevelBase):
    pass

class LevelInDB(LevelBase):
    id: int

    class Config:
        orm_mode = True

class LevelsResponseModel(BaseModel):
    data: List[LevelInDB]
    pagination: Pagination
from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.base import Student
from app.schemas import (
    StudentCreate,
    StudentUpdate,
)

class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    pass


student = CRUDStudent(Student)

from email.policy import default
from enum import unique
from sqlalchemy import (
    Column,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import SmallInteger
from app.db.base_class import Base


class Grade(Base):
    id = Column(SmallInteger, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    numeric_value = Column(SmallInteger, nullable=False)
    subjects = relationship('GradeSubject', back_populates='grade', cascade="all, delete-orphan")
    students = relationship('Registration', back_populates='grade')

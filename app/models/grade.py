from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import SmallInteger
from app.db.base_class import Base


class Grade(Base):
    __table_args__ = (
        UniqueConstraint('name', 'level_id', name='name_level_uc'),
    )
    id = Column(SmallInteger, primary_key=True, index=True, autoincrement=False)
    name = Column(String, index=True, nullable=False)
    numeric_value = Column(SmallInteger, nullable=False)
    level_id = Column(ForeignKey('levels.id'), nullable=False)
    notes = Column(String, nullable=True)
    subjects = relationship('Subject', back_populates='grades', secondary="subject_grades")
    students = relationship('Registration', back_populates='grade')
    level = relationship('Level', back_populates='grades', lazy="selectin")
    assigned_teachers = relationship('AssignedTeacher', back_populates='grade')
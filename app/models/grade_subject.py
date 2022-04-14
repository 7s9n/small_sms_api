from sqlalchemy import (
    Column,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class GradeSubject(Base):
    grade_id = Column(ForeignKey('grades.id'), primary_key=True)
    subject_id = Column(ForeignKey('subjects.id'), primary_key=True)

    grade = relationship('Grade', back_populates='subjects')
    subject = relationship('Subject', back_populates='grades')
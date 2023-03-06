from sqlalchemy import (
    Column,
    ForeignKey,
    Table,
)
# from sqlalchemy.orm import relationship
from app.db.base_class import Base

subject_grades = Table('subject_grades', Base.metadata,
    Column('grade_id', ForeignKey('grades.id'), primary_key=True),
    Column('subject_id', ForeignKey('subjects.id'), primary_key=True)
)

# class GradeSubject(Base):
    
#     grade_id = Column(ForeignKey('grades.id'), primary_key=True)
#     subject_id = Column(ForeignKey('subjects.id'), primary_key=True)

    # grade = relationship('Grade', back_populates='subjects')
    # subject = relationship('Subject', back_populates='grades')
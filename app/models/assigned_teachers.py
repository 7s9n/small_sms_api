from sqlalchemy import (
    Column,
    ForeignKey,
    String,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger
from app.db.base_class import Base



class AssignedTeacher(Base):
    teacher_id = Column(ForeignKey('users.id'), nullable=False)
    grade_id = Column(ForeignKey('grades.id'), primary_key=True)
    subject_id = Column(ForeignKey('subjects.id'), primary_key=True)
    school_year_id = Column(ForeignKey('schoolyears.id'), primary_key=True)
    

    teacher = relationship('User', back_populates='teacher_assigned_grades_and_subjects', lazy="joined")
    grade = relationship("Grade", back_populates='assigned_teachers', lazy="joined")
    subject = relationship("Subject", back_populates='assigned_teachers',lazy="joined")
    school_year = relationship("SchoolYear")

    # proxies
    teacher_name = association_proxy(target_collection='teacher', attr='first_name')
    subject_name = association_proxy(target_collection='subject', attr='name')
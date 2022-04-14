from sqlalchemy import (
    Column,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import BigInteger
from ..db.base_class import Base


class Registration(Base):
    id = Column(BigInteger, primary_key=True)
    regi_no = Column(String, nullable=False)
    student_id = Column(ForeignKey('students.id'), nullable=False)
    grade_id = Column(ForeignKey('grades.id'), nullable=False)
    school_year_id = Column(ForeignKey('schoolyears.id'), nullable=False)
    old_registration_id = Column(ForeignKey('registrations.id'), nullable=True)

    student = relationship('Student', back_populates='registrations')
    grade = relationship("Grade", back_populates='students')
    school_year = relationship("SchoolYear")
    old_registration = relationship("Registration", remote_side=[id])
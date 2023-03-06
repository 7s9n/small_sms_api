from sqlalchemy import (
    Column,
    String,
    ForeignKey,
    Integer,
    DateTime,
    table,
    column
)
from sqlalchemy.ext.hybrid import hybrid_property
import datetime
from sqlalchemy import func
from app.db.base_class import Base


class Mark(Base):
    student_id = Column(ForeignKey('users.id'), primary_key=True)
    grade_id = Column(ForeignKey('grades.id'), primary_key=True)
    subject_id = Column(ForeignKey('subjects.id'), primary_key=True)
    school_year_id = Column(ForeignKey('schoolyears.id'), primary_key=True)
    semaster = Column(Integer, primary_key=True)
    month = Column(Integer, primary_key=True)

    written_test = Column(Integer, nullable=False)
    oral_test = Column(Integer, nullable=False)
    homeworks = Column(Integer, nullable=False)
    attendance = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, 
        server_default=func.now(),
        server_onupdate=func.now()
    )

    notes = Column(String, nullable=True)

    @hybrid_property
    def total(self)-> float:
        return self.written_test + self.attendance + self.oral_test + self.homeworks
    
    @hybrid_property
    def monthly_outcome(self)-> float:
        return round(self.total) / 5
    @monthly_outcome.expression
    def monthly_outcome(self)-> float:
        return func.round(self.total) / 5
    # old_registration_id = Column(ForeignKey('registrations.id'), nullable=True)

    # student = relationship('User', back_populates='registrations')
    # grade = relationship("Grade", back_populates='students')
    # school_year = relationship("SchoolYear", back_populates='students')
    # old_registration = relationship("Registration", remote_side=[id])

class FinalMark(Base):
    student_id = Column(ForeignKey('users.id'), primary_key=True)
    subject_id = Column(ForeignKey('subjects.id'), primary_key=True)
    semaster = Column(Integer, primary_key=True)
    school_year_id = Column(ForeignKey('schoolyears.id'), primary_key=True)
    exam = Column(Integer, nullable=False)


monthly_mark_report = table(
    "monthly_mark_report",
    column("student_id"),
    column("student_name"),
    column("grade_id"),
    column("grade_name"),
    column("subject_id"),
    column("subject_name"),
    column("school_year_id"),
    column("school_year_title"),
    column("month"),
    column("semaster"),
    column("attendance"),
    column("oral_test"),
    column("homeworks"),
    column("written_test"),
    column("total"),
    column("monthly_outcome"),
    column("grading"),
)

final_mark_report = table(
    "final_mark_report",
    column("student_id"),
    column("student_name"),
    column("subject_id"),
    column("school_year_id"),
    column("semaster"),
    column("exam"),
    column("final_outcome"),
)

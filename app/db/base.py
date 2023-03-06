# Import all the models, so that Base has them before being
# imported by Alembic

from app.db.base_class import Base
from app.models.grade_subject import subject_grades
from app.models.grade import Grade  # noqa
from app.models.subject import Subject  # noqa
from app.models.school_year import SchoolYear  # noqa
# from app.models.student import Student  # noqa
# from app.models.grade_subject import GradeSubject  # noqa
from app.models.registration import Registration  # noqa
from app.models.nationality import Nationality  # noqa
from app.models.levels import Level # noqa
from app.models.grading_scale import GradingScale # noqa
# from app.models.person import Person
from app.models.user import User # noqa
from app.models.marks import  (
    Mark,
    FinalMark,
)
from app.models import (
    AssignedTeacher,
)
# from app.models.admin import Admin # noqa
# from app.models.teacher import Teacher #noqa
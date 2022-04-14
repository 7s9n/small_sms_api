# Import all the models, so that Base has them before being
# imported by Alembic

from db.base_class import Base
from models.grade import Grade  # noqa
from models.subject import Subject  # noqa
from models.school_year import SchoolYear  # noqa
from models.student import Student  # noqa
from models.grade_subject import GradeSubject  # noqa
from models.registration import Registration  # noqa
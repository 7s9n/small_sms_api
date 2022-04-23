# Import all the models, so that Base has them before being
# imported by Alembic

from app.db.base_class import Base
from app.models.grade import Grade  # noqa
from app.models.subject import Subject  # noqa
from app.models.school_year import SchoolYear  # noqa
from app.models.student import Student  # noqa
from app.models.grade_subject import GradeSubject  # noqa
from app.models.registration import Registration  # noqa
from app.models.nationality import Nationality  # noqa
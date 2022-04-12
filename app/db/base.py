# Import all the models, so that Base has them before being
# imported by Alembic

from app.db.base_class import Base
from app.models.grade import Grade  # noqa
from app.models.subject import Subject  # noqa
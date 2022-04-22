from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal


def get_db() -> Generator:
    try:
        db: Session = SessionLocal()
        yield db
    finally:
        db.close()


class CommonQueryParams:
    def __init__(self, skip: int = 0, limit: int = 100) -> None:
        self.skip = skip
        self.limit = limit

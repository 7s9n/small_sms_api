from fastapi import APIRouter
from app.api.api_v1.routes import (
    grade,
    registration,
    subject,
    school_year,
    student,
)

api_router = APIRouter()

api_router.include_router(grade.router)
api_router.include_router(subject.router)
api_router.include_router(school_year.router)
api_router.include_router(student.router)
api_router.include_router(registration.router)
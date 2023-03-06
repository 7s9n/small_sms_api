from fastapi import APIRouter
from app.api.api_v1.routes import (
    grade,
    registration,
    subject,
    school_year,
    student,
    nationality,
    levels,
    subject_grade,
    grading_scale,
    user,
    login,
    teacher,
    mark,
    dashboard
)

api_router = APIRouter()

api_router.include_router(login.router)
api_router.include_router(dashboard.router)
api_router.include_router(teacher.router)
api_router.include_router(mark.router)
api_router.include_router(user.router)
api_router.include_router(grading_scale.router)
api_router.include_router(subject_grade.router)
api_router.include_router(grade.router)
api_router.include_router(subject.router)
api_router.include_router(school_year.router)
api_router.include_router(student.router)
api_router.include_router(registration.router)
api_router.include_router(nationality.router)
api_router.include_router(levels.router)

from fastapi import APIRouter
from app.api.api_v1.routes import (
    grade,
    subject,
)

api_router = APIRouter()

api_router.include_router(grade.router)
api_router.include_router(subject.router)
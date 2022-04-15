from fastapi import APIRouter
from app.api.api_v1.routes import grade

api_router = APIRouter()

api_router.include_router(grade.router)
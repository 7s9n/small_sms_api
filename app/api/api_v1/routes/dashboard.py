from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from sqlalchemy.orm import Session, aliased
from sqlalchemy import func
from app.api import deps
from app import (
    crud,
    schemas,
    models,
)
router = APIRouter(prefix='/dashboard', tags=['Dashboard'])

@router.get("/")
def dashboard(
    *,
    db: Session = Depends(deps.get_db),
):
    current_school_year = crud.school_year.get_current_school_year(db)
    current_school_year_id = current_school_year.id if current_school_year else 0

    student_count = crud.user.get_student_count_by_school_year_id(db, current_school_year_id)

    male_student_count = crud.user.get_male_student_count_by_school_year_id(db, current_school_year_id)

    grade_count = len(crud.grade.get_multi(db))

    teacher_count = len(crud.user.get_all_teachers(db))

    return {
        "studentCount": student_count,
        "maleStudentCount": male_student_count,
        "teacherCount": teacher_count,
        "gradeCount": grade_count,
    }
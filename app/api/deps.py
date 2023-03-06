from typing import (
    Generator,
    Dict,
    Optional,
)

from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.resources.strings import (
    THRER_IS_NO_CURRENT_ACTIVE_SCHOOL_YEAR,
    SUBJECT_DOES_NOT_EXIST,
    STUDENT_DOES_NOT_EXIST,
    SCHOOL_YEAR_DOES_NOT_EXIST,
    GRADE_DOES_NOT_EXIST,
    MARKS_NOT_FOUND,
    TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
    LEVEL_DOES_NOT_EXIST,
)
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db: Session = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="تعذر التحقق من صحة بيانات الاعتماد.",
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود.")
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="مستخدم غير نشط.")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="المستخدم ليس لديه امتيازات كافية."
        )
    return current_user


def get_current_active_teacher(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if not crud.user.is_teacher(current_user):
        raise HTTPException(
            status_code=400, detail="المستخدم ليس لديه امتيازات كافية."
        )
    return current_user


def get_current_active_student(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if not crud.user.is_student(current_user):
        raise HTTPException(
            status_code=400, detail="المستخدم ليس لديه امتيازات كافية."
        )
    return current_user


def get_current_active_teacher_or_admin(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if crud.user.is_student(current_user):
        raise HTTPException(
            status_code=400, detail="المستخدم ليس لديه امتيازات كافية."
        )
    return current_user


def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = crud.user.get(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STUDENT_DOES_NOT_EXIST
        )
    return student


def get_grade_by_id(grade_id: int, db: Session = Depends(get_db)):
    grade = crud.grade.get(db, grade_id)
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=GRADE_DOES_NOT_EXIST
        )
    return grade


def get_subject_by_id(subject_id: int, db: Session = Depends(get_db)):
    subject = crud.subject.get(db, subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=SUBJECT_DOES_NOT_EXIST
        )
    return subject


def get_level_by_id(level_id: int, db: Session = Depends(get_db)):
    level = crud.level.get(db, level_id)
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=LEVEL_DOES_NOT_EXIST
        )
    return level


def get_current_active_school_year(db: Session = Depends(get_db)):
    current_school_year = crud.school_year.get_current_school_year(db)
    if not current_school_year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=THRER_IS_NO_CURRENT_ACTIVE_SCHOOL_YEAR
        )
    return current_school_year


def get_school_year_by_id(school_year_id: int, db: Session = Depends(get_db)):
    school_year = crud.school_year.get(db, school_year_id)
    if not school_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=SCHOOL_YEAR_DOES_NOT_EXIST
        )
    return school_year


def get_registration_by_pk(student_id: int, school_year_id: int, db: Session = Depends(get_db)):
    registration = crud.registeration.get(db, {
        "student_id": student_id,
        "school_year_id": school_year_id,
    })
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"التسجيل الذي تحاول الوصول له غير موجود في النظام."
        )
    return registration


def get_final_mark(
    student_id: int,
    semaster: schemas.SemasterEnum,
    subject_id: int,
    current_school_year: models.SchoolYear = Depends(
        get_current_active_school_year),
    db: Session = Depends(get_db),
):
    final_mark = db.query(models.FinalMark).get(
        {
        "student_id": student_id,
        "semaster": semaster,
        "subject_id": subject_id,
        "school_year_id": current_school_year.id,
        }
    )
    if not final_mark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MARKS_NOT_FOUND,
        )
    return final_mark

def get_mark(
    student_id: int,
    month: schemas.MonthEnum,
    semaster: schemas.SemasterEnum,
    grade_id: int,
    subject_id: int,
    current_school_year: models.SchoolYear = Depends(
        get_current_active_school_year),
    db: Session = Depends(get_db),
):
    mark = crud.mark.get_by_pk(
        db,
        {
            "student_id": student_id,
            "month": month,
            "semaster": semaster,
            "grade_id": grade_id,
            "subject_id": subject_id,
            "school_year_id": current_school_year.id
        }
    )
    if not mark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MARKS_NOT_FOUND,
        )
    return mark


def get_query_school_year_id_or_default(
    *,
    db: Session = Depends(get_db),
    school_year_id: int = Query(default=None)
):
    if not school_year_id:
        school_year_id = crud.school_year.get_current_school_year(db)

    return school_year_id


def teacher_has_permission_to_access_mark(
    *,
    db: Session = Depends(get_db),
    teacher: models.User = Depends(get_current_active_teacher),
    current_school_year: models.SchoolYear = Depends(
        get_current_active_school_year),
    grade_id: int,
    subject_id: int,
):
    has_permission_to_create_or_update_mark = crud.mark.has_permission_to_create_or_update_mark(
        db=db,
        teacher_id=teacher.id,
        subject_id=subject_id,
        grade_id=grade_id,
        school_year_id=current_school_year.id
    )
    if not has_permission_to_create_or_update_mark:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
        )


class PaginationQuery:
    def __init__(
            self,
            page: int = Query(default=..., ge=1),
            limit: int = Query(default=..., le=50),
    ) -> None:
        self.page = page
        self.limit = limit


class CommonQueryParams:
    def __init__(
            self,
            page: int = Query(default=None, ge=1),
            limit: int = Query(default=None, le=50),
            search: str = Query(default="")
    ) -> None:
        self.page = page
        self.limit = limit
        self.search = search

# class CommonQueryParams:
#     def __init__(self, skip: int = 0, limit: int = 100) -> None:
#         self.skip = skip
#         self.limit = limit

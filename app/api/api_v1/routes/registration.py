from typing import (
    List,
    Optional,
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from sqlalchemy.orm import Session
from app.api.deps import CommonQueryParams, get_db
from app import (
    crud,
    schemas,
)
router = APIRouter(prefix='/registrations', tags=['Registrations'])


@router.get('', response_model=List[schemas.RegistrationOut])
def get_registrations(
    *,
    db: Session = Depends(get_db),
    commons: CommonQueryParams = Depends(),
    school_year_id: Optional[int] = None,
    grade_id: Optional[int] = None,
    regi_no: Optional[str] = None,
):
    params = dict(grade_id=grade_id,
                  school_year_id=school_year_id, regi_no=regi_no)

    return crud.registeration.get_multi(
        db, skip=commons.skip,
        limit=commons.limit, params=params
    )


@router.get('/{registration_id}', response_model=schemas.RegistrationOut)
def get_registration(
    *,
    db: Session = Depends(get_db),
    registration_id: int
):
    registration = crud.registeration.get(db, registration_id)

    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registration with id {registration_id} does not exist."
        )
    return registration


@router.post('', response_model=schemas.RegistrationOut, status_code=status.HTTP_201_CREATED)
def create_registration(
    *,
    db: Session = Depends(get_db),
    registration_in: schemas.RegistrationIn
):
    school_year = crud.school_year.get_current_school_year(db)

    if not school_year:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"School year not set yet! Please go to settings and set it."
        )

    student = crud.student.get(db, registration_in.student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Student with id {registration_in.student_id} does not exist.'
        )

    grade = crud.grade.get(db, registration_in.grade_id)

    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Grade with id {registration_in.grade_id} does not exist.'
        )

    reg = crud.registeration.get_registration_by_grade_student_school_year(
        db, student_id=student.id,
        school_year_id=school_year.id
    )

    if reg:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot register student in two classes on the same year."
        )

    # Generate a unique registration number
    regi_no = crud.registeration.generate_unique_regi_no(
        db, school_year, grade)

    registration_data = schemas.RegistrationCreate(
        regi_no=regi_no, student_id=student.id,
        grade_id=grade.id, school_year_id=school_year.id
    )

    registration = crud.registeration.create(db, obj_in=registration_data)
    return registration

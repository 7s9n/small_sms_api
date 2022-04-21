from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app import (
    crud,
    schemas,
)
from app.schemas.school_year import SchoolYearInDB
router = APIRouter(prefix='/school-years', tags=['School Years'])


@router.get('', response_model=List[schemas.SchoolYearInDB])
def get_school_years(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """
    Retrieve all school years.
    """
    school_years = crud.school_year.get_multi(db, skip=skip, limit=limit)
    return school_years


@router.get('/{school_year_id}', response_model=schemas.SchoolYearInDB)
def get_school_year(
    *,
    db: Session = Depends(get_db),
    school_year_id: int,
):
    """
    Retrieve one school year based on id key.
    """
    school_year = crud.school_year.get(db, id=school_year_id)

    if not school_year:
        raise HTTPException(
            status_code=404, detail=f"School year with id {school_year_id} does not exist",
        )
    return school_year


@router.post('',  status_code=status.HTTP_201_CREATED)
def create_school_year(
    *,
    db: Session = Depends(get_db),
    school_year_in: schemas.SchoolYearCreate
):
    """
    Create a school year.
    """
    school_year = crud.school_year.get_by_name(db, name=school_year_in.title)

    if school_year:
        raise HTTPException(
            status_code=409, detail="A school year with this name already exists",
        )

    school_year = crud.school_year.create(db, obj_in=school_year_in)
    return school_year


@router.put('/{school_year_id}', response_model=schemas.SchoolYearInDB)
def update_school_year(
    *,
    db: Session = Depends(get_db),
    school_year_id: int,
    school_year_in: schemas.SchoolYearUpdate
):
    """
    Update a school year.
    """
    school_year = crud.school_year.get(db, id=school_year_id)

    if not school_year:
        raise HTTPException(
            status_code=404, detail=f"School year with id {school_year_id} does not exist",
        )

    school_year = crud.school_year.update(
        db, db_obj=school_year, obj_in=school_year_in)
    return school_year


@router.put('/{school_year_id}/activate', response_model=schemas.SchoolYearInDB)
def activate_school_year(
    *,
    db: Session = Depends(get_db),
    school_year_id: int
):
    """
    Set current school year
    """
    school_year = crud.school_year.get(db, school_year_id)

    if not school_year:
        raise HTTPException(
            status_code=404, detail=f"School year with id {school_year_id} does not exist",
        )

    school_year = crud.school_year.acivate_school_year(db, school_year_id)

    return school_year


@router.delete('/{school_year_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_school_year(
    *,
    db: Session = Depends(get_db),
    school_year_id: int,
):
    """
    Delete a school year.
    """
    school_year = crud.school_year.get(db, id=school_year_id)

    if not school_year:
        raise HTTPException(
            status_code=404, detail=f"School year with id {school_year_id} does not exist",
        )
    if school_year.students:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"لايمكن حذف هذا العالم الدراسي {school_year.title} لانه توجد بيانات طلاب مرتبطة به, يجب حذف بيانات الطلاب اولاُ ثم حاول مرة اخرى.",
        )

    school_year = crud.school_year.remove(db, id=school_year_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

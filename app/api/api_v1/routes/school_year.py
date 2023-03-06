from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from sqlalchemy.orm import Session

from app.api.deps import get_db, CommonQueryParams
from app.api import deps
from app import (
    crud,
    schemas,
    models,
)
from app.resources.strings import (
    SCHOOL_YEAR_DOES_NOT_EXIST,
    THERE_IS_DEPENDENT_DATA_ERROR,
)
# from app.schemas.school_year import SchoolYearResponseModel
router = APIRouter(prefix='/school-years', tags=['School Years'])

@router.get('/active', response_model=schemas.SchoolYearInDB)
def get_current_school_year(db: Session = Depends(get_db), user: models.User = Depends(deps.get_current_active_user)):
    return crud.school_year.get_current_school_year(db)

@router.get('', response_model=schemas.SchoolYearResponseModel | List[schemas.SchoolYearInDB])
def get_school_years(
    *,
    db: Session = Depends(get_db),
    queryParam: CommonQueryParams = Depends(),
    user: models.User = Depends(deps.get_current_active_user)
):
    """
    Retrieve all school years.
    """
    if queryParam.page is None or queryParam.limit is None:
        return crud.school_year.get_multi(db=db)

    num_of_rows, school_years = crud.school_year.get_multi_paginated(
        db, page=queryParam.page, limit=queryParam.limit, 
        filters={"title": queryParam.search}
    )

    return schemas.SchoolYearResponseModel(
        data=school_years,
        pagination={
            "current_page": queryParam.page,
            "per_page": queryParam.limit,
            "total_records": num_of_rows,
        }
        # len(school_years) if queryParam.search != '' else crud.school_year.count(db)
    )


@router.get('/{school_year_id}', response_model=schemas.SchoolYearInDB)
def get_school_year(
    *,
    school_year: models.SchoolYear = Depends(deps.get_school_year_by_id),
    user: models.User = Depends(deps.get_current_active_user),
):
    """
    Retrieve one school year based on id key.
    """
    # school_year = crud.school_year.get(db, id=school_year_id)

    # if not school_year:
    #     raise HTTPException(
    #         status_code=404, detail=f"العام الدراسي الذي تبحث عنه غير موجود",
    #     )
    return school_year


@router.post('',  status_code=status.HTTP_201_CREATED)
def create_school_year(
    *,
    db: Session = Depends(get_db),
    school_year_in: schemas.SchoolYearCreate,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Create a school year.
    """
    school_year = crud.school_year.get_by_name(db, name=school_year_in.title)

    if school_year:
        raise HTTPException(
            status_code=409, detail="يوجد عام دراسي بهذا الأسم من قبل.",
        )

    school_year = crud.school_year.create(db, obj_in=school_year_in)
    crud.school_year.acivate_school_year(db, school_year.id)
    return school_year


@router.put('/{school_year_id}', response_model=schemas.SchoolYearInDB)
def update_school_year(
    *,
    db: Session = Depends(get_db),
    school_year_id: int,
    school_year_in: schemas.SchoolYearUpdate,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Update a school year.
    """
    school_year = crud.school_year.get_by_name(db, name=school_year_in.title)

    if school_year and school_year.id != school_year_id:
        raise HTTPException(
            status_code=409, detail="يوجد عام دراسي بهذا الأسم من قبل.",
        )

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
    school_year_id: int,
    user: models.User = Depends(deps.get_current_active_superuser),
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
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Delete a school year.
    """
    school_year = crud.school_year.get(db, id=school_year_id)

    if not school_year:
        raise HTTPException(
            status_code=404, detail=SCHOOL_YEAR_DOES_NOT_EXIST,
        )
    if school_year.students:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=THERE_IS_DEPENDENT_DATA_ERROR,
        )
    previous_school_year = None
    if school_year.is_active:
        previous_school_year = crud.school_year.get_previous_school_year(db)

    school_year = crud.school_year.remove(db, payload=school_year_id)
    
    if previous_school_year:
        crud.school_year.acivate_school_year(db, previous_school_year.id)

    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

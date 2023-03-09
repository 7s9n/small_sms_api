from typing import (
    List,
    Union,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from app import models
from sqlalchemy.orm import Session

from app.api import deps
from app import (
    crud,
    schemas,
)
from app.resources.strings import (
    THERE_IS_DEPENDENT_DATA_ERROR,
    NATIONALITY_DOES_NOT_EXIST,
)
router = APIRouter(prefix='/nationalities', tags=['Nationalities'])


@router.get('', response_model=Union[schemas.NationalitiesResponseModel,List[schemas.NationalityInDB]])
def get_nationalities(
    *,
    db: Session = Depends(deps.get_db),
    queryParam: deps.CommonQueryParams = Depends(),
    user: models.User = Depends(deps.get_current_active_user),
):
    """
    Retrieve nationalities.
    """
    if queryParam.page is None or queryParam.limit is None:
        return crud.nationality.get_multi(db)

    num_of_rows, nationalities = crud.nationality.get_multi_paginated(
        db=db, page=queryParam.page, limit=queryParam.limit,
        filters={"masculine_form": queryParam.search, "feminine_form": queryParam.search}
    )
    if not nationalities:
        return []
    return schemas.NationalitiesResponseModel(
        data=nationalities,
        pagination= {
            "current_page": queryParam.page,
            "per_page": queryParam.limit,
            "total_records": num_of_rows,
        }
    )



@router.get('/{nationality_id}', response_model=schemas.NationalityInDB)
def get_nationality(
    *,
    db: Session = Depends(deps.get_db),
    nationality_id: int,
    user: models.User = Depends(deps.get_current_active_user),
):
    """
    Get nationality by id.
    """
    nationality = crud.nationality.get(db, nationality_id)

    if not nationality:
        raise HTTPException(status_code=404, detail=NATIONALITY_DOES_NOT_EXIST)

    return nationality


@router.post('', response_model=schemas.NationalityInDB, status_code=status.HTTP_201_CREATED)
def create_nationality(
    *,
    db: Session = Depends(deps.get_db),
    nationality_in: schemas.NationalityCreate,
    admin: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Create new nationality.
    """
    nationality = crud.nationality.get_by_name(
        db, nationality_in.masculine_form, nationality_in.feminine_form
    )
    if nationality:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="يوجد جنسية بـ هذه البيانات مسبقاً.")

    nationality = crud.nationality.create(db, obj_in=nationality_in)

    return nationality


@router.put('/{nationality_id}', response_model=schemas.NationalityInDB)
def update_nationality(
    *,
    db: Session = Depends(deps.get_db),
    nationality_id: int,
    nationality_in: schemas.NationalityUpdate,
    admin: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Update a nationality.
    """
    nationality = crud.nationality.get(db, nationality_id)

    if not nationality:
        raise HTTPException(status_code=404, detail=NATIONALITY_DOES_NOT_EXIST)

    nationality = crud.nationality.get_by_name(
        db, nationality_in.masculine_form, nationality_in.feminine_form
    )
    if nationality and nationality.id != nationality_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"يوجد جنسية بـ هذه البيانات مسبقاً."
        )
    nationality = crud.nationality.update(
        db, db_obj=nationality, obj_in=nationality_in)

    return nationality


@router.delete('/{nationality_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_nationality(
    *,
    db: Session = Depends(deps.get_db),
    nationality_id: int,
    admin: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Delete a nationality.
    """
    nationality = crud.nationality.get(db, nationality_id)

    if not nationality:
        raise HTTPException(status_code=404, detail=NATIONALITY_DOES_NOT_EXIST)

    if nationality.users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=THERE_IS_DEPENDENT_DATA_ERROR
        )

    crud.nationality.remove(db, payload=nationality_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

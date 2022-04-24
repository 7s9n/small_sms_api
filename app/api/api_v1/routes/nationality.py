from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from sqlalchemy.orm import Session

from app.api import deps
from app import (
    crud,
    schemas,
)

router = APIRouter(prefix='/nationalities', tags=['Nationalities'])


@router.get('', response_model=List[schemas.NationalityInDB])
def get_nationalities(
    *,
    db: Session = Depends(deps.get_db),
    commons: deps.CommonQueryParams = Depends(),
):
    """
    Retrieve nationalities.
    """
    return crud.nationality.get_multi(db, skip=commons.skip, limit=commons.limit)


@router.get('/{nationality_id}', response_model=schemas.NationalityInDB)
def get_nationality(
    *,
    db: Session = Depends(deps.get_db),
    nationality_id: int
):
    """
    Get nationality by id.
    """
    nationality = crud.nationality.get(db, nationality_id)

    if not nationality:
        raise HTTPException(status_code=404, detail="Nationality not found")

    return nationality


@router.post('', response_model=schemas.NationalityInDB, status_code=status.HTTP_201_CREATED)
def create_nationality(
    *,
    db: Session = Depends(deps.get_db),
    nationality_in: schemas.NationalityCreate
):
    """
    Create new nationality.
    """
    nationality = crud.nationality.get_by_name(
        db, nationality_in.masculine_form, nationality_in.feminine_form
    )
    if nationality:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Redundant data.")

    nationality = crud.nationality.create(db, obj_in=nationality_in)

    return nationality


@router.put('/{nationality_id}', response_model=schemas.NationalityInDB)
def update_nationality(
    *,
    db: Session = Depends(deps.get_db),
    nationality_id: int,
    nationality_in: schemas.NationalityUpdate
):
    """
    Update a nationality.
    """
    nationality = crud.nationality.get(db, nationality_id)

    if not nationality:
        raise HTTPException(status_code=404, detail="Nationality not found")

    nationality = crud.nationality.get_by_name(
        db, nationality_in.masculine_form, nationality_in.feminine_form
    )
    if nationality and nationality.id != nationality_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Redundant data."
        )
    nationality = crud.nationality.update(
        db, db_obj=nationality, obj_in=nationality_in)

    return nationality


@router.delete('/{nationality_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_nationality(
    *,
    db: Session = Depends(deps.get_db),
    nationality_id: int,
):
    """
    Delete a nationality.
    """
    nationality = crud.nationality.get(db, nationality_id)

    if not nationality:
        raise HTTPException(status_code=404, detail="Nationality not found")

    if nationality.students:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There are students data depends on this nationality."
        )

    crud.nationality.remove(db, id=nationality_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

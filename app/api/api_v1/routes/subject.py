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
router = APIRouter(prefix='/subjects', tags=['Subjects'])


@router.get('', response_model=List[schemas.SubjectInDB])
def get_subjects(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """
    Retrieve all subjects.
    """
    subjects = crud.subject.get_multi(db, skip=skip, limit=limit)
    return subjects


@router.get('/{subject_id}', response_model=schemas.SubjectInDB)
def get_subject(
    *,
    db: Session = Depends(get_db),
    subject_id: int,
):
    """
    Retrieve one subject based on id key.
    """
    subject = crud.subject.get(db, id=subject_id)

    if not subject:
        raise HTTPException(
            status_code=404, detail=f"Subject with id {subject_id} does not exist",
        )

    return subject


@router.post('', response_model=schemas.SubjectInDB, status_code=status.HTTP_201_CREATED)
def create_subject(
    *,
    db: Session = Depends(get_db),
    subject_in: schemas.SubjectCreate
):
    """
    Create a subject.
    """
    subject = crud.subject.get_by_name(db, name=subject_in.name)

    if subject:
        raise HTTPException(
            status_code=409, detail="A subject with this name already exists",
        )

    subject = crud.subject.create(db, obj_in=subject_in)
    return subject


@router.put('/{subject_id}', response_model=schemas.SubjectInDB)
def update_subject(
    *,
    db: Session = Depends(get_db),
    subject_id: int,
    subject_in: schemas.SubjectUpdate
):
    """
    Update a subject.
    """
    subject = crud.subject.get(db, id=subject_id)

    if not subject:
        raise HTTPException(
            status_code=404, detail=f"Subject with id {subject_id} does not exist",
        )

    subject = crud.subject.update(db, db_obj=subject, obj_in=subject_in)
    return subject


@router.delete('/{subject_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    *,
    db: Session = Depends(get_db),
    subject_id: int,
):
    """
    Delete a subject.
    """
    subject = crud.subject.get(db, id=subject_id)

    if not subject:
        raise HTTPException(
            status_code=404, detail=f"Subject with id {subject_id} does not exist",
        )

    subject = crud.subject.remove(db, id=subject_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

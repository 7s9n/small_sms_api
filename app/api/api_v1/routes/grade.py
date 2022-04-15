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
router = APIRouter(prefix='/grades', tags=['Grades'])


@router.get('', response_model=List[schemas.GradeInDB])
def get_grades(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """
    Retrieve all grades.
    """
    grades = crud.grade.get_multi(db, skip=skip, limit=limit)
    return grades


@router.get('/{grade_id}', response_model=schemas.GradeInDB)
def get_grade(
    *,
    db: Session = Depends(get_db),
    grade_id: int,
):
    """
    Retrieve one grade based on id key.
    """
    grade = crud.grade.get(db, id=grade_id)

    if not grade:
        raise HTTPException(
            status_code=404, detail=f"Grade with id {grade_id} does not exist",
        )

    return grade


@router.post('', response_model=schemas.GradeInDB, status_code=status.HTTP_201_CREATED)
def create_grade(
    *,
    db: Session = Depends(get_db),
    grade_in: schemas.GradeCreate
):
    """
    Create a grade.
    """
    grade = crud.grade.get_by_name(db, name=grade_in.name)

    if grade:
        raise HTTPException(
            status_code=409, detail="A grade with this name already exists",
        )

    grade = crud.grade.create(db, obj_in=grade_in)
    return grade


@router.put('/{grade_id}', response_model=schemas.GradeInDB)
def update_grade(
    *,
    db: Session = Depends(get_db),
    grade_id: int,
    grade_in: schemas.GradeUpdate
):
    """
    Update a grade.
    """
    grade = crud.grade.get(db, id=grade_id)

    if not grade:
        raise HTTPException(
            status_code=404, detail=f"Grade with id {grade_id} does not exist",
        )

    grade = crud.grade.update(db, db_obj=grade, obj_in=grade_in)
    return grade


@router.delete('/{grade_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(
    *,
    db: Session = Depends(get_db),
    grade_id: int,
):
    """
    Delete a grade.
    """
    grade = crud.grade.get(db, id=grade_id)

    if not grade:
        raise HTTPException(
            status_code=404, detail=f"Grade with id {grade_id} does not exist",
        )

    grade = crud.grade.remove(db, id=grade_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

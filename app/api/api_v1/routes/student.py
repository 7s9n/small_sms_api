from typing import List
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
router = APIRouter(prefix='/students', tags=['Students'])


@router.get('', response_model=List[schemas.StudentInDB])
def get_students(
    *,
    db: Session = Depends(get_db),
    commons: CommonQueryParams = Depends(),
):
    return crud.student.get_multi(db, skip=commons.skip, limit=commons.limit)


@router.get('/{student_id}', response_model=schemas.StudentInDB)
def get_student(
    *,
    db: Session = Depends(get_db),
    student_id: int,
):
    student = crud.student.get(db, student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} does not exist."
        )
    return student


@router.post('', response_model=schemas.StudentInDB, status_code=status.HTTP_201_CREATED)
def create_student(
    *,
    db: Session = Depends(get_db),
    student_in: schemas.StudentCreate
):

    student = crud.student.create(db, obj_in=student_in)
    return student


@router.put('/{student_id}', response_model=schemas.StudentInDB)
def update_student(
    *,
    db: Session = Depends(get_db),
    student_id: int,
    student_in: schemas.StudentUpdate
):
    student = crud.student.get(db, student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} does not exist."
        )
    student = crud.student.update(db, db_obj=student, obj_in=student_in)

    return student


@router.delete('/{student_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    *,
    db: Session = Depends(get_db),
    student_id: int
):
    student = crud.student.get(db, student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} does not exist."
        )

    if student.registrations:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete this student because, it has data depends on it."
        )
    # check if student has not marks then delete it

    crud.student.remove(db, id=student_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

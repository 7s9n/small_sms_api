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
from app.db.base import(
    GradeSubject,
    Subject,
    Grade
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


@router.post('/subjects', response_model=schemas.GradeSubjectOut)
def assign_subject_to_grade(
    *,
    db: Session = Depends(get_db),
    grade_subject_in: schemas.GradeSubjectCreate
):
    grade = crud.grade.get(db, grade_subject_in.grade_id)
    subject = crud.subject.get(db, grade_subject_in.subject_id)
    grade_subject = crud.grade_subject.get(
        db, grade_subject_in.grade_id, grade_subject_in.subject_id
    )

    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grade with id {grade_subject_in.grade_id} does not exist",
        )

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Subject with id {grade_subject_in.subject_id} does not exist'
        )
    if grade_subject:
        raise HTTPException(
            status_code=409, detail=f"{grade_subject.subject.name} has already assigned to {grade_subject.grade.name}",
        )
    grade_subject = crud.grade_subject.create(db, obj_in=grade_subject_in)

    return {
        'grade': grade,  # grade_subject.grade
        'subject': subject  # grade_subject.subject
    }


@router.get('/{grade_id}/subjects', response_model=schemas.GradeSubjectsOut)
def get_assigned_or_not_assigned_grade_subjects(
    *,
    db: Session = Depends(get_db),
    grade_id: int,
    assigned: bool = True
):
    grade = crud.grade.get(db, grade_id)
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grade with id {grade_id} does not exist",
        )
    subjects = crud.grade.get_grade_assigned_or_not_assigned_subjects(
        db, grade_id=grade_id, assigned=assigned
    )
    return {
        'grade': grade,
        'subjects': subjects
    }


@router.put('/{grade_id}/subjects/{subject_id}', status_code=status.HTTP_501_NOT_IMPLEMENTED)
def update_grade_subject(
    *,
    db: Session = Depends(get_db),
    grade_id: int,
    subject_id: int,
    grade_subject_in: schemas.GradeSubjectUpdate
):
    pass


@router.delete('/{grade_id}/subjects/{subject_id}', status_code=status.HTTP_204_NO_CONTENT)
def unassign_subject_from_grade(
    *,
    db: Session = Depends(get_db),
    grade_id: int,
    subject_id: int,
):
    grade = crud.grade.get(db, grade_id)
    subject = crud.subject.get(db, subject_id)
    grade_subject = crud.grade_subject.get(db, grade_id, subject_id)

    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grade with id {grade_id} does not exist",
        )
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Subject with id {subject_id} does not exist'
        )
    if not grade_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{subject.name} is not assigned to {grade.name}.'
        )

    crud.grade_subject.remove(db, grade_id=grade_id, subject_id=subject_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

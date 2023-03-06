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

from app.api.deps import (
    get_db,
    CommonQueryParams,
)
from app.api import deps
from app import (
    crud,
    schemas,
    models,
)
from app.db.base import subject_grades

router = APIRouter(prefix='/subject-grade', tags=['Subject Grade'])


@router.get('/', response_model=List[schemas.SubjectsGradeSchema],)
def get_all(
    *, 
    db: Session = Depends(get_db), 
    grade_id: Optional[int] = None, 
    user: models.User = Depends(deps.get_current_active_user),
):
    return crud.grade.get_multi(db, params={"id": grade_id})


@router.get('/{grade_id}', response_model=schemas.SubjectsGradeSchema)
def get_grade_subject_by_id(
    *, 
    db: Session = Depends(get_db), 
    grade_id: int,
    user: models.User = Depends(deps.get_current_active_user),
):
    return crud.grade.get(db, grade_id)


@router.get('/{grade_id}/subjects', response_model=schemas.SubjectsGradeSchema)
def get_assigned_or_not_assigned_subjects(*,
                                          db: Session = Depends(get_db),
                                          grade_id: int,
                                          assigned: bool = True,
                                          user: models.User = Depends(deps.get_current_active_teacher_or_admin),):
    grade = crud.grade.get(db, grade_id)

    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"الصف رقم {grade_id} غير موجود",
        )
    subjects = crud.grade.get_grade_assigned_or_not_assigned_subjects(
        db, grade_id=grade_id, assigned=assigned)

    return schemas.SubjectsGradeSchema(
        id=grade.id, name=grade.name,
        level_id=grade.level_id,
        level=grade.level,
        numeric_value=grade.numeric_value,
        subjects=subjects,
    )


@router.post('/', response_model=schemas.SubjectsGradeSchema, status_code=status.HTTP_201_CREATED)
def create_subject_grade(
    *,
    db: Session = Depends(get_db),
    payload: schemas.GradeSubjectCreate,
    admin: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Assign subject to grade.
    """
    grade = crud.grade.get(db, payload.grade_id)

    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"الصف رقم {payload.grade_id} غير موجود",
        )
    subject = crud.subject.get(db, payload.subject_id)

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'المادة رقم {payload.subject_id} غير موجودة'
        )
    stmt = subject_grades.select().where(subject_grades.c.grade_id == payload.grade_id,
                                         subject_grades.c.subject_id == payload.subject_id)
    grade_subject = db.execute(stmt).first()
    if grade_subject:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'مادة {subject.name} قد تم تخصيصها مسبقاً للصف {grade.name}'
        )
    grade.subjects.append(subject)
    db.add(grade)
    db.commit()
    db.refresh(grade)

    return grade


@router.delete('/{grade_id}/{subject_id}', status_code=status.HTTP_204_NO_CONTENT)
def remove_subject_from_grade(
    *,
    db: Session = Depends(get_db),
    grade: models.Grade = Depends(deps.get_grade_by_id),
    subject: models.Subject = Depends(deps.get_subject_by_id),
    admin: models.User = Depends(deps.get_current_active_superuser),
):
    stmt = subject_grades.select().where(
        subject_grades.c.grade_id == grade.id,
        subject_grades.c.subject_id == subject.id
    )
    grade_subject = db.execute(stmt).first()
    if not grade_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'لايوجد مادة او فصل بالمعرفات التي قمت بتزويدها مرتبطه ببعضها.'
        )

    can_be_deleted = db.query(models.AssignedTeacher).filter(
        models.AssignedTeacher.grade_id == grade.id,
        models.AssignedTeacher.subject_id == subject.id,
    ).all()

    if can_be_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="لايمكنك الحذف, هناك سجلات تعتمد على هذه البيانات."
        )
    stmt = subject_grades.delete().where(
        subject_grades.c.grade_id == grade.id,
        subject_grades.c.subject_id == subject.id
    )
    db.execute(stmt)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

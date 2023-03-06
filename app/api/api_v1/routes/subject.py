from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from sqlalchemy.orm import Session,aliased
from sqlalchemy import func

from app.api.deps import get_db, CommonQueryParams
from app.api import deps
from app import (
    crud,
    schemas,
    models,
)
from app.resources.strings import (
    THERE_IS_DEPENDENT_DATA_ERROR,
    SUBJECT_DOES_NOT_EXIST,
    GRADE_DOES_NOT_EXIST,
    TEACHER_DOES_NOT_EXIST,
)
router = APIRouter(prefix='/subjects', tags=['Subjects'])


@router.get('', response_model=schemas.SubjectsResponseModel | List[schemas.SubjectInDB])
def get_subjects(
    *,
    db: Session = Depends(get_db),
    queryParam: CommonQueryParams = Depends(),
    user: models.User = Depends(deps.get_current_active_user),
):
    """
    Retrieve all subjects.
    """
    if queryParam.page is None or queryParam.limit is None:
        return crud.subject.get_multi(db=db)

    num_of_rows, subjects = crud.subject.get_multi_paginated(
        db, page=queryParam.page, limit=queryParam.limit,
        filters={"name": queryParam.search}
    )
    if not subjects:
        return []
    return schemas.SubjectsResponseModel(
        data=subjects,
        pagination= {
            "current_page": queryParam.page,
            "per_page": queryParam.limit,
            "total_records": num_of_rows,
        }
    )

from pydantic import BaseModel, Field
class Subject(BaseModel):
    id: int = Field(alias='subject_id')
    name: str = Field(alias='subject_name')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        
class Teacher(BaseModel):
    id: int = Field(alias="teacher_id")
    name: str = Field(alias='teacher_name')

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class TeacherSubjectList(BaseModel):
    teacher: schemas.UserInDBase
    subjects: List[schemas.SubjectInDB]

    class Config:
        orm_mode = True


class TeacherAssignedSubjectsAndGrades(BaseModel):
    subject_id: int
    subject_name: str
    grade_id: int
    grade_name: str
    school_year_id: int

    class Config:
        orm_mode = True

@router.get('/teacher', response_model=List[TeacherAssignedSubjectsAndGrades])
def get_teacher_subjects(
    *, 
    db:Session = Depends(get_db),
    teacher_id: Optional[int] = None,
    grade_id: Optional[int] = None,
    current_user: models.User = Depends(deps.get_current_active_teacher_or_admin),
    current_school_year: models.SchoolYear = Depends(deps.get_current_active_school_year)
):
    teacher = None
    if current_user.role == 't':
        teacher_id = current_user.id
        teacher = current_user

    elif teacher_id is None and current_user.role == 'a':
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="يجب إدخال المعرف الخاص بالمدرس لعرض المواد الخاصة به."
        )
    if not teacher:
        teacher = crud.user.get(db, teacher_id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=TEACHER_DOES_NOT_EXIST,
            )
    
    
    a1 = aliased(models.AssignedTeacher)
    query = db.query(
        models.Subject.id.label("subject_id"),
        models.Subject.name.label("subject_name"),
        models.Grade.id.label("grade_id"),
        func.concat(models.Grade.name, " ", models.Level.name).label("grade_name"),
        a1.school_year_id,
    ).select_from(a1).\
        join(
            models.Subject, 
            models.Subject.id == a1.subject_id
        ).join(
            models.Grade, 
            models.Grade.id == a1.grade_id
        ).join(
            models.Level,
            models.Level.id == models.Grade.level_id
        ).\
            filter(
                a1.teacher_id == teacher_id,
                a1.school_year_id == current_school_year.id,
            )
    if grade_id:
        grade = crud.grade.get(db, grade_id)
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=GRADE_DOES_NOT_EXIST,
            )
        query = query.filter(a1.grade_id == grade_id)
        
    return query.all()
    


@router.get('/{subject_id}', response_model=schemas.SubjectInDB)
def get_subject(
    *,
    db: Session = Depends(get_db),
    subject_id: int,
    user: models.User = Depends(deps.get_current_active_user),
):
    """
    Retrieve one subject based on id key.
    """
    subject = crud.subject.get(db, id=subject_id)

    if not subject:
        raise HTTPException(
            status_code=404, detail=f"المادة الذي تبحث عنها غير موجودة",
        )

    return subject


@router.post('', response_model=schemas.SubjectInDB, status_code=status.HTTP_201_CREATED)
def create_subject(
    *,
    db: Session = Depends(get_db),
    subject_in: schemas.SubjectCreate,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Create a subject.
    """
    subject = crud.subject.get_by_name(db, name=subject_in.name)

    if subject:
        raise HTTPException(
            status_code=409, detail=f"يوجد مادة دراسية  بهذا الاسم ({subject_in.name}) بالفعل",
        )
    subject = crud.subject.get_by_name(db, name=subject_in.foreign_name)

    if subject:
        raise HTTPException(
            status_code=409, detail=f"يوجد مادة دراسية  بهذا الاسم ({subject_in.foreign_name}) بالفعل",
        )
    subject = crud.subject.create(db, obj_in=subject_in)
    return subject


@router.put('/{subject_id}', response_model=schemas.SubjectInDB)
def update_subject(
    *,
    db: Session = Depends(get_db),
    subject_id: int,
    subject_in: schemas.SubjectUpdate,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Update a subject.
    """
    subject = crud.subject.get_by_name(db, name=subject_in.name)

    if subject and subject.id != subject_id:
        raise HTTPException(
            status_code=409, detail=f"يوجد مادة دراسية  بهذا الاسم ({subject_in.name}) بالفعل",
        )
    subject = crud.subject.get_by_name(db, name=subject_in.foreign_name)

    if subject and subject.id != subject_id:
        raise HTTPException(
            status_code=409, detail=f"يوجد مادة دراسية  بهذا الاسم ({subject_in.foreign_name}) بالفعل",
        )

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
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Delete a subject.
    """
    subject = crud.subject.get(db, id=subject_id)
    if not subject:
        raise HTTPException(
            status_code=404, detail=SUBJECT_DOES_NOT_EXIST,
        )
    if subject.grades or subject.assigned_teachers:
        raise HTTPException(
            status_code=409, 
            detail=THERE_IS_DEPENDENT_DATA_ERROR,
        )
    subject = crud.subject.remove(db, payload=subject_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


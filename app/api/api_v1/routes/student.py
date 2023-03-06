from typing import (
    List,
    Union,
    Optional,
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased
from app.api.deps import CommonQueryParams, get_db
from app.api import deps
from app import (
    crud,
    schemas,
    models,
)
from app.resources.strings import (
    THERE_IS_DEPENDENT_DATA_ERROR,
)
router = APIRouter(prefix='/students', tags=['Students'])


@router.get('/', response_model=Union[schemas.StudentPaginatedResponse, List[schemas.StudentInDB]])
def get_students(
    *,
    db: Session = Depends(get_db),
    queryParam: CommonQueryParams = Depends(),
    admin_user = Depends(deps.get_current_active_superuser)
):
    
    if queryParam.page is None or queryParam.limit is None:
        return crud.user.get_all_students(db=db)
    
    students, num_of_rows = crud.user.get_paginated_users(
        db=db, page=queryParam.page, limit=queryParam.limit,
        search=queryParam.search,
        roles=['s'],
    )
    if not students:
        return []
    return schemas.StudentPaginatedResponse(
        data=students,
        pagination={
            "current_page": queryParam.page,
            "per_page": queryParam.limit,
            "total_records": num_of_rows,
        }
    )

@router.get('/marks/{subject_id}/{school_year_id}')
def get_subject_marks_of_student(
    *,
    db: Session = Depends(deps.get_db),
    subject_id: int,
    school_year_id: int,
    month: Optional[schemas.MonthEnum] = None,
    semaster: Optional[schemas.SemasterEnum] = None,
    student: models.User = Depends(deps.get_current_active_student),
):
    params = {
        "subject_id": subject_id,
        "month": month,
        "semaster": semaster,
        "school_year_id": school_year_id,
        "student_id": student.id,
    }
    query = db.query(models.monthly_mark_report)
    for attr in [x for x in params if params[x] is not None]:
        query = query.filter(getattr(models.monthly_mark_report.c, attr) == params[attr])
    monthly_marks = query.all()

    query = db.query(models.final_mark_report)

    for attr in [x for x in params if params[x] is not None]:
        if attr != 'month':
            query = query.filter(getattr(models.final_mark_report.c, attr) == params[attr])
    
    final_marks = query.all()

    return {
        "monthly_marks": monthly_marks,
        "final_marks" : final_marks,
    }
@router.get('/registrations', response_model=List[schemas.StudentRegistrations])
def get_student_registrations(
    *,
    db: Session = Depends(deps.get_db),
    student: models.User = Depends(deps.get_current_active_student)
):
    a1 = aliased(models.Registration)
    query = db.query(
        models.Grade.id.label("grade_id"),
        func.concat(models.Grade.name, " ",
                    models.Level.name).label("grade_name"),
        models.SchoolYear.id.label("school_year_id"),
        models.SchoolYear.title.label("school_year_title"),
    ).select_from(a1)\
        .join(
            models.SchoolYear,
            models.SchoolYear.id == a1.school_year_id,
        ).join(
            models.Grade,
            models.Grade.id == a1.grade_id,
        ).join(
            models.Level,
            models.Grade.level_id == models.Level.id,
        ).filter(
            a1.student_id == student.id
        )
    return query.all() 


@router.get('/subjects')
def get_student_subjects(
    *,
    db: Session = Depends(deps.get_db),
    school_year_id: int = Depends(deps.get_query_school_year_id_or_default),
    student: models.User = Depends(deps.get_current_active_student)
):
    if not school_year_id:
        return []
    
    grade_id = db.query(
        models.Registration.grade_id
    ).get({
        "student_id": student.id,
        "school_year_id": school_year_id
    })
    return 
    

@router.get('/{student_id}', response_model=schemas.StudentInDB)
def get_student(
    *,
    db: Session = Depends(get_db),
    student_id: int,
    user: models.User = Depends(deps.get_current_active_user),
):
    student = crud.user.get(db, student_id)

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
    student_in: schemas.StudentCreate,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    if not crud.nationality.get(db, student_in.nationality_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nationality with id {student_in.nationality_id} not found."
        )
    student = crud.user.get_by_username(db, username=student_in.username)
    if student:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"موجود بالفعل في النظام {student_in.username} اسم المستخدم",
        )
    student = crud.user.create_student(db, obj_in=student_in)
    return student


@router.put('/{student_id}', response_model=schemas.StudentInDB)
def update_student(
    *,
    db: Session = Depends(get_db),
    student_id: int,
    student_in: schemas.StudentUpdate,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    updated_student = crud.user.get_student(db, student_id)

    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} does not exist."
        )

    student = crud.user.get_by_username(db, username=student_in.username)
    if student and student.id != student_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"موجود بالفعل في النظام {student_in.username} اسم المستخدم",
        )
    
    if not crud.nationality.get(db, student_in.nationality_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nationality with id {student_in.nationality_id} not found."
        )
    
    student = crud.user.update(db, db_obj=updated_student, obj_in=student_in)

    return student


@router.delete('/{student_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    *,
    db: Session = Depends(get_db),
    student_id: int,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    student = crud.user.get_student(db, student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} does not exist."
        )

    if student.registrations:
        raise HTTPException(
            status_code=409, 
            detail=THERE_IS_DEPENDENT_DATA_ERROR,
        )
    # check if student has no marks then delete it
    
    crud.user.remove(db, payload=student_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

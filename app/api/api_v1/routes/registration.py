from typing import (
    List,
    Optional,
    Union,
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy import exists, text
from sqlalchemy.orm import Session, joinedload
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
router = APIRouter(prefix='/registrations', tags=['Registrations'])

@router.get('', response_model=Union[schemas.RegistrationsResponseModel, List[schemas.RegistrationOut]])
def get_registrations(
    *,
    db: Session = Depends(get_db),
    queryParam: CommonQueryParams = Depends(),
    school_year_id: Optional[int] = None,
    grade_id: Optional[int] = None,
    user: models.User = Depends(deps.get_current_active_teacher_or_admin),
):
    if not school_year_id:
        school_year = crud.school_year.get_current_school_year(db)
        if not school_year:
            return []
        school_year_id = school_year.id

    if queryParam.page is None or queryParam.limit is None:
        return crud.registeration.get_multi(db=db, params={"school_year_id": school_year_id, "grade_id": grade_id})
    
    num_of_rows, registrations = crud.registeration.get_multi_paginated(
        db, page=queryParam.page, limit=queryParam.limit,
        params={"school_year_id": school_year_id, "grade_id": grade_id},
        sort_by="created_at",
    )
    if not registrations:
        return []
    
    return {
        "data":registrations,
        "pagination": {
            "current_page": queryParam.page,
            "per_page": queryParam.limit,
            "total_records": num_of_rows,
        }
    }


@router.get('/students/unregistered', response_model=List[schemas.StudentInDB], response_model_include=['id', "full_name"])
def get_unregistered_students(
    *,
    db: Session = Depends(get_db),
    user: models.User = Depends(deps.get_current_active_teacher_or_admin),
):
    school_year = crud.school_year.get_current_school_year(db)
    if not school_year:
        return []

    query = db.query(models.User).filter(
        models.User.role == 's'
    ).filter(
        ~exists().where(
            models.User.id == models.Registration.student_id,
            models.Registration.school_year_id == school_year.id,
        )
    ).order_by(models.User.full_name)

    return query.all()
    
@router.post('', response_model=schemas.RegistrationOut, status_code=status.HTTP_201_CREATED)
def create_registration(
    *,
    db: Session = Depends(get_db),
    registration_in: schemas.RegistrationIn,
    admin: models.User = Depends(deps.get_current_active_superuser),
):
    school_year = crud.school_year.get_current_school_year(db)

    if not school_year:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"السنة الدراسية لم تحدد بعد! يرجى الذهاب إلى الإعدادات وتعيينها."
        )

    student = crud.user.get(db, registration_in.student_id)

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'الطالب الذي ارسلته غير موجود في النظام'
        )

    grade = crud.grade.get(db, registration_in.grade_id)

    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'الصف الذي ارسلته غير موجود في النظام'
        )

    reg = crud.registeration.get_registration_by_grade_student_school_year(
        db, student_id=student.id,
        school_year_id=school_year.id
    )

    if reg:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"لا يمكن تسجيل الطالب في فصلين في نفس العام."
        )

    registration_data = schemas.RegistrationCreate(
        student_id=student.id,
        grade_id=grade.id, school_year_id=school_year.id
    )

    registration = crud.registeration.create(
        db, obj_in=registration_data, has_id=False)
    return registration

@router.delete('/{student_id}/{school_year_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_registration(
    *,
    db: Session = Depends(get_db),
    student: models.User = Depends(deps.get_student_by_id),
    school_year: models.SchoolYear = Depends(deps.get_school_year_by_id),
    registration: models.Registration = Depends(deps.get_registration_by_pk),
    admin: models.User = Depends(deps.get_current_active_superuser),
):
    current_school_year = crud.school_year.get_current_school_year(db)
    if school_year.id != current_school_year.id:
        raise HTTPException(
            status_code=400,
            detail="هذه البيانات للقراء فقط, لايمكنك حذفها"
        )
    ## check if student has no marks then delete it
    if crud.mark.get_by_custom_filters(
        db,
        filters={
            "grade_id": registration.grade_id,
            "student_id": registration.student_id,
            "school_year_id": school_year.id
        }
    ):
        raise HTTPException(status_code=400, detail=THERE_IS_DEPENDENT_DATA_ERROR)

    crud.registeration.remove(
        db, 
        payload=dict(student_id=student.id, school_year_id=school_year.id)
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

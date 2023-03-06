from typing import (
    Optional,
    Dict
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, desc
from app.api.deps import get_db
from app.api import deps
from app.resources import strings
from app import (
    crud,
    schemas,
    models,
)
from app.resources.strings import (
    TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
    STUDENT_DOES_NOT_EXIST,
    REDUNDANT_DATA,
    MARKS_NOT_FOUND,
)
router = APIRouter(prefix='/marks', tags=['Marks'])


@router.get('/', response_model=schemas.MarksResponseModel)
def get_marks(
    *,
    db: Session = Depends(deps.get_db),
    current_school_year: models.SchoolYear = Depends(
        deps.get_current_active_school_year),
    teacher: models.User = Depends(deps.get_current_active_teacher),
    pagination_query: deps.PaginationQuery = Depends(),
    grade_id: int,
    subject_id: int,
    month: Optional[schemas.MonthEnum] = None,
    semaster: Optional[schemas.SemasterEnum] = None,
    student_id: Optional[int] = None,
):
    # Check if teacher has permission for assigning this marks
    has_permission_to_create_or_update_mark = crud.mark.has_permission_to_create_or_update_mark(
        db=db,
        teacher_id=teacher.id,
        subject_id=subject_id,
        grade_id=grade_id,
        school_year_id=current_school_year.id
    )

    if not has_permission_to_create_or_update_mark:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
        )
    params = {
        "grade_id": grade_id,
        "subject_id": subject_id,
        "month": month,
        "semaster": semaster,
        "school_year_id": current_school_year.id,
        "student_id": student_id,
    }
    # return db.execute("select* from monthly_mark_report").all()
    a1 = aliased(models.Mark)
    query = db.query(
        models.User.id.label("student_id"),
        func.concat(models.User.first_name, " ", models.User.father_name, " ",
                    models.User.gfather_name, " ", models.User.last_name).label("student_name"),
        models.Grade.id.label("grade_id"),
        func.concat(models.Grade.name, " ",
                    models.Level.name).label("grade_name"),
        models.Subject.id.label("subject_id"),
        models.Subject.name.label("subject_name"),
        models.SchoolYear.id.label("school_year_id"),
        models.SchoolYear.title.label("school_year_title"),
        a1.month,
        a1.semaster,
        a1.attendance,
        a1.oral_test,
        a1.homeworks,
        a1.written_test,
        a1.school_year_id,
        a1.total,
        a1.monthly_outcome,
    ).select_from(a1).\
        join(
            models.User,
            models.User.id == a1.student_id,
    ).join(
            models.Grade,
            models.Grade.id == a1.grade_id,
    ).join(
            models.Level,
            models.Level.id == models.Grade.level_id,
    ).join(
            models.Subject,
            models.Subject.id == a1.subject_id,
    ).join(
        models.SchoolYear,
        models.SchoolYear.id == a1.school_year_id,
    )

    for attr in [x for x in params if params[x] is not None]:
        query = query.filter(getattr(a1, attr) == params[attr])

    number_of_rows = query.count()
    rows = query.order_by(desc("student_name")).offset(
        (pagination_query.page - 1) * pagination_query.limit).limit(pagination_query.limit).all()
    return {
        "data": rows,
        "pagination": {
            "current_page": pagination_query.page,
            "per_page": pagination_query.limit,
            "total_records": number_of_rows,
        }
    }


@router.get('/final')
def get_final_marks(
    *,
    db: Session = Depends(deps.get_db),
    current_school_year: models.SchoolYear = Depends(
        deps.get_current_active_school_year),
    teacher: models.User = Depends(deps.get_current_active_teacher),
    pagination_query: deps.PaginationQuery = Depends(),
    grade_id: int,
    subject_id: int,
    semaster: Optional[schemas.SemasterEnum] = None,
    student_id: Optional[int] = None,
):
    # Check if teacher has permission for assigning this marks
    has_permission_to_create_or_update_mark = crud.mark.has_permission_to_create_or_update_mark(
        db=db,
        teacher_id=teacher.id,
        subject_id=subject_id,
        grade_id=grade_id,
        school_year_id=current_school_year.id
    )

    if not has_permission_to_create_or_update_mark:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
        )
    params = {
        "subject_id": subject_id,
        "semaster": semaster,
        "school_year_id": current_school_year.id,
        "student_id": student_id,
    }
    query = db.query(models.final_mark_report)
    for attr in [x for x in params if params[x] is not None]:
        query = query.filter(
            getattr(models.final_mark_report.c, attr) == params[attr])

    number_of_rows = query.count()
    rows = query.order_by(models.final_mark_report.c.student_name).offset(
        (pagination_query.page - 1) * pagination_query.limit).limit(pagination_query.limit).all()
    return {
        "data": rows,
        "pagination": {
            "current_page": pagination_query.page,
            "per_page": pagination_query.limit,
            "total_records": number_of_rows,
        }
    }


@router.get('/final/{student_id}/{semaster}/{subject_id}/{grade_id}')
def get_student_final_mark(
    *,
    db: Session = Depends(deps.get_db),
    student_id: int,
    semaster: schemas.SemasterEnum,
    subject_id: int,
    grade_id: int,
    current_school_year: models.SchoolYear = Depends(
        deps.get_current_active_school_year),
    teacher: models.User = Depends(deps.get_current_active_teacher),
):
    # Check if teacher has permission for accessing this marks
    has_permission_to_create_or_update_mark = crud.mark.has_permission_to_create_or_update_mark(
        db=db,
        teacher_id=teacher.id,
        subject_id=subject_id,
        grade_id=grade_id,
        school_year_id=current_school_year.id
    )

    if not has_permission_to_create_or_update_mark:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
        )

    final_mark = db.query(models.final_mark_report).\
        filter(
        models.final_mark_report.c.student_id == student_id,
        models.final_mark_report.c.subject_id == subject_id,
        models.final_mark_report.c.semaster == semaster,
        models.final_mark_report.c.school_year_id == current_school_year.id,
    ).first()

    if not final_mark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MARKS_NOT_FOUND,
        )
    return final_mark


@router.get('/{student_id}/{month}/{semaster}/{subject_id}/{grade_id}')
def get_student_mark(
    *,
    db: Session = Depends(deps.get_db),
    student_id: int,
    month: schemas.MonthEnum,
    semaster: schemas.SemasterEnum,
    grade_id: int,
    subject_id: int,
    current_school_year: models.SchoolYear = Depends(
        deps.get_current_active_school_year),
    teacher: models.User = Depends(deps.get_current_active_teacher),
):
    # Check if teacher has permission for assigning this marks
    has_permission_to_create_or_update_mark = crud.mark.has_permission_to_create_or_update_mark(
        db=db,
        teacher_id=teacher.id,
        subject_id=subject_id,
        grade_id=grade_id,
        school_year_id=current_school_year.id
    )

    if not has_permission_to_create_or_update_mark:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
        )

    a1 = aliased(models.Mark)
    query = db.query(
        models.User.id.label("student_id"),
        func.concat(models.User.first_name, " ", models.User.father_name, " ",
                    models.User.gfather_name, " ", models.User.last_name).label("student_name"),
        models.Grade.id.label("grade_id"),
        func.concat(models.Grade.name, " ",
                    models.Level.name).label("grade_name"),
        models.Subject.id.label("subject_id"),
        models.Subject.name.label("subject_name"),
        models.SchoolYear.id.label("school_year_id"),
        models.SchoolYear.title.label("school_year_title"),
        a1.month,
        a1.semaster,
        a1.attendance,
        a1.oral_test,
        a1.homeworks,
        a1.written_test,
        a1.school_year_id,
        a1.total,
        a1.monthly_outcome,
    ).select_from(a1).\
        join(
            models.User,
            models.User.id == a1.student_id,
    ).join(
            models.Grade,
            models.Grade.id == a1.grade_id,
    ).join(
            models.Level,
            models.Level.id == models.Grade.level_id,
    ).join(
            models.Subject,
            models.Subject.id == a1.subject_id,
    ).join(
        models.SchoolYear,
        models.SchoolYear.id == a1.school_year_id,
    ).filter(
        a1.student_id == student_id,
        a1.school_year_id == current_school_year.id,
        a1.subject_id == subject_id,
        a1.grade_id == grade_id,
        a1.month == month,
        a1.semaster == semaster,
    )
    mark = query.first()
    if not mark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=MARKS_NOT_FOUND,
        )
    return mark


@router.post('/final', status_code=status.HTTP_201_CREATED)
def create_student_final_mark(
    *,
    db: Session = Depends(get_db),
    mark_in: schemas.FinalMarkCreateRequest,
    current_school_year: models.SchoolYear = Depends(
        deps.get_current_active_school_year),
    teacher: models.User = Depends(deps.get_current_active_teacher),
):
    # Check if teacher has permission for assigning this marks
    has_permission_to_create_or_update_mark = crud.mark.has_permission_to_create_or_update_mark(
        db=db,
        teacher_id=teacher.id,
        subject_id=mark_in.subject_id,
        grade_id=mark_in.grade_id,
        school_year_id=current_school_year.id
    )
    if not has_permission_to_create_or_update_mark:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
        )

    mark_in_db = schemas.FinalMarkCreateInDB(
        **{**mark_in.dict(exclude={"grade_id"}), "school_year_id": current_school_year.id}
    )

    # Check if student registration exists
    student = crud.registeration.get_by_custom_filters(
        db,
        filters={
            "student_id": mark_in_db.student_id,
            "grade_id": mark_in.grade_id,
            "school_year_id": mark_in_db.school_year_id,
        }
    )
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STUDENT_DOES_NOT_EXIST,
        )

    # Check if data is already submitted.

    is_already_exists = db.query(models.FinalMark).get(
        mark_in_db.dict(include={"student_id",
                                 "subject_id", "school_year_id", "semaster"}),
    )
    if is_already_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=REDUNDANT_DATA,
        )
    db_obj = None
    try:
        obj_in_data = jsonable_encoder(mark_in_db)
        db_obj = models.FinalMark(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    except Exception as e:
        raise HTTPException(500, "خطاء في السرفر لايمكن إضافة هذه البيانات, حاول مرة اخرى.")

    return db_obj



@router.post('/', status_code=status.HTTP_201_CREATED)
def create_student_mark(
    *,
    db: Session = Depends(get_db),
    mark_in: schemas.MarkCreateRequest,
    current_school_year: models.SchoolYear = Depends(
        deps.get_current_active_school_year),
    teacher: models.User = Depends(deps.get_current_active_teacher),
):
    # Check if teacher has permission for assigning this marks
    has_permission_to_create_or_update_mark = crud.mark.has_permission_to_create_or_update_mark(
        db=db,
        teacher_id=teacher.id,
        subject_id=mark_in.subject_id,
        grade_id=mark_in.grade_id,
        school_year_id=current_school_year.id
    )
    if not has_permission_to_create_or_update_mark:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
        )

    mark_in_db = schemas.MarkCreateInDB(
        **{**mark_in.dict(), "school_year_id": current_school_year.id}
    )
    # Check if student registration exists
    student = crud.registeration.get_by_custom_filters(
        db,
        filters={
            "student_id": mark_in_db.student_id,
            "grade_id": mark_in_db.grade_id,
            "school_year_id": mark_in_db.school_year_id,
        }
    )
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=STUDENT_DOES_NOT_EXIST,
        )

    # Check if data is already submitted.
    is_already_exists = crud.mark.get_by_pk(
        db,
        mark_in_db.dict(include={"student_id", "grade_id",
                        "subject_id", "school_year_id", "semaster", "month"}),
    )
    if is_already_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=REDUNDANT_DATA,
        )

    mark = crud.mark.create(db, obj_in=mark_in_db, has_id=False)
    return mark

@router.put('/final/{student_id}/{semaster}/{subject_id}/{grade_id}')
def update_student_final_mark(
    *,
    db: Session = Depends(get_db),
    teacher: models.User = Depends(deps.get_current_active_teacher),
    current_school_year: models.SchoolYear = Depends(
        deps.get_current_active_school_year),
    mark: models.final_mark_report = Depends(deps.get_final_mark),
    grade_id: int,
    mark_in: schemas.FinalMarkUpdate,
):
    # Check if teacher has permission for assigning this marks
    has_permission_to_create_or_update_mark = crud.mark.has_permission_to_create_or_update_mark(
        db=db,
        teacher_id=teacher.id,
        subject_id=mark.subject_id,
        grade_id=grade_id,
        school_year_id=current_school_year.id
    )
    if not has_permission_to_create_or_update_mark:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
        )
    obj_data = jsonable_encoder(mark)
    update_data = mark_in.dict(exclude_unset=True)
    for field in obj_data:
            if field in update_data:
                setattr(mark, field, update_data[field])
    
    db.add(mark)
    db.commit()
    db.refresh(mark)
    return mark

@router.put('/{student_id}/{month}/{semaster}/{subject_id}/{grade_id}')
def update_student_mark(
    *,
    db: Session = Depends(get_db),
    teacher: models.User = Depends(deps.get_current_active_teacher),
    current_school_year: models.SchoolYear = Depends(
        deps.get_current_active_school_year),
    mark: models.Mark = Depends(deps.get_mark),
    mark_in: schemas.MarkUpdate,
):
    # Check if teacher has permission for assigning this marks
    has_permission_to_create_or_update_mark = crud.mark.has_permission_to_create_or_update_mark(
        db=db,
        teacher_id=teacher.id,
        subject_id=mark.subject_id,
        grade_id=mark.grade_id,
        school_year_id=current_school_year.id
    )
    if not has_permission_to_create_or_update_mark:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
        )
    mark = crud.mark.update(db, db_obj=mark, obj_in=mark_in)
    return mark

@router.delete('/final/{student_id}/{semaster}/{subject_id}/{grade_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_student_final_mark(
    *,
    db: Session = Depends(deps.get_db),
    mark: models.FinalMark = Depends(deps.get_final_mark),
    grade_id: int,
    current_school_year: models.SchoolYear = Depends(
        deps.get_current_active_school_year),
    teacher: models.User = Depends(deps.get_current_active_teacher),
):
    has_permission_to_create_or_update_mark = crud.mark.has_permission_to_create_or_update_mark(
        db=db,
        teacher_id=teacher.id,
        subject_id=mark.subject_id,
        grade_id=grade_id,
        school_year_id=current_school_year.id
    )
    if not has_permission_to_create_or_update_mark:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
        )
    db.delete(mark)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete('/{student_id}/{month}/{semaster}/{subject_id}/{grade_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_student_mark(
    *,
    db: Session = Depends(deps.get_db),
    mark: models.Mark = Depends(deps.get_mark),
    current_school_year: models.SchoolYear = Depends(
        deps.get_current_active_school_year),
    teacher: models.User = Depends(deps.get_current_active_teacher)
):
    has_permission_to_create_or_update_mark = crud.mark.has_permission_to_create_or_update_mark(
        db=db,
        teacher_id=teacher.id,
        subject_id=mark.subject_id,
        grade_id=mark.grade_id,
        school_year_id=current_school_year.id
    )
    if not has_permission_to_create_or_update_mark:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TEACHER_UNAUTHORIZED_TO_ACCESS_MARKS,
        )
    final_mark = db.query(models.FinalMark).get(
        {
        "student_id": mark.student_id,
        "semaster": mark.semaster,
        "subject_id": mark.subject_id,
        "school_year_id": current_school_year.id,
        }
    )
    if final_mark:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strings.THERE_IS_DEPENDENT_DATA_ERROR,
        )
    db.delete(mark)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

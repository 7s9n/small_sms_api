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

from sqlalchemy.orm import Session, aliased
from sqlalchemy import func
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
from app.resources.strings import (
    TEACHER_DOES_NOT_EXIST,
    LEVEL_DOES_NOT_EXIST,
    GRADE_DOES_NOT_EXIST,
)
router = APIRouter(prefix='/grades', tags=['Grades'])



@router.get('', response_model=Union[schemas.GradesResponseModel , List[schemas.GradeInDB]])
async def get_grades(
    *,
    db: Session = Depends(get_db),
    queryParam: CommonQueryParams = Depends(),
    user: models.User = Depends(deps.get_current_active_user)
):
    """
    Retrieve all grades.
    """
    if queryParam.page is None or queryParam.limit is None:
        return crud.grade.get_multi(db=db)

    num_of_rows, grades = crud.grade.get_multi_paginated(
        db, page=queryParam.page, limit=queryParam.limit,
        filters={"name": queryParam.search}
    )
    if not grades:
        return []
    return schemas.GradesResponseModel(
        data=grades,
        pagination= {
            "current_page": queryParam.page,
            "per_page": queryParam.limit,
            "total_records": num_of_rows,
        }
    )

@router.get('/teacher', response_model=List[schemas.BasicGradeInfo],\
    response_model_exclude={"level", "name"}
)
def get_teacher_assigned_grades(
    *,
    db: Session = Depends(deps.get_db),
    teacher_id: Optional[int] = None,
    current_user: models.User = Depends(deps.get_current_active_teacher_or_admin),
    current_school_year: models.SchoolYear = Depends(deps.get_current_active_school_year)
):
    """
    Retrieve all teacher assigned grades for the current year
    """
    teacher = None
    if current_user.role == 't':
        teacher_id = current_user.id
        teacher = current_user

    elif teacher_id is None and current_user.role == 'a':
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="يجب إدخال المعرف الخاص بالمدرس لعرض الصفوف الخاصة به."
        )
    if not teacher:
        teacher = crud.user.get(db, teacher_id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=TEACHER_DOES_NOT_EXIST,
            )
    
    a1 = aliased(models.AssignedTeacher)
    grades = db.query(
        models.Grade.id.label("id"),
        func.concat(models.Grade.name, " ",
                    models.Level.name).label("composite_name"),
    ).select_from(a1).\
        join(
            models.Grade,
            models.Grade.id == a1.grade_id,
        ).join(
            models.Level,
            models.Level.id == models.Grade.level_id,
        ).filter(
            a1.teacher_id==teacher_id,
            a1.school_year_id == current_school_year.id
        ).all()

    # subquery = db.query(
    #     models.AssignedTeacher.grade_id
    # ).filter(
    #     models.AssignedTeacher.teacher_id==teacher_id,
    #     models.AssignedTeacher.school_year_id == current_school_year.id
    # ).subquery()

    # grades = db.query(
    #     models.Grade
    # ).filter(models.Grade.id.in_(subquery)).all()

        
    return grades

@router.get('/{grade_id}', response_model=schemas.GradeInDB)
def get_grade(
    *,
    db: Session = Depends(get_db),
    grade_id: int,
    user: models.User = Depends(deps.get_current_active_user),
):
    """
    Retrieve one grade based on id key.
    """
    grade = crud.grade.get(db, id=grade_id)

    if not grade:
        raise HTTPException(
            status_code=404, detail=GRADE_DOES_NOT_EXIST,
        )

    return grade


@router.post('', response_model=schemas.GradeInDB, status_code=status.HTTP_201_CREATED)
def create_grade(
    *,
    db: Session = Depends(deps.get_db),
    grade_in: schemas.GradeCreate,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Create a grade.
    """
    if not crud.level.get(db, grade_in.level_id):
        raise HTTPException(
            status_code=404, detail=LEVEL_DOES_NOT_EXIST,
        )

    grade = crud.grade.get_by_name_and_level(db, name=grade_in.name, level_id=grade_in.level_id)

    if grade:
        raise HTTPException(
            status_code=409, detail="يوجد صف بنفس الاسم في نفس المرحلة الدراسية.",
        )

    grade = crud.grade.create(db, obj_in=grade_in)
    return grade


@router.put('/{grade_id}', response_model=schemas.GradeInDB)
def update_grade(
    *,
    db: Session = Depends(get_db),
    grade_id: int,
    grade_in: schemas.GradeUpdate,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Update a grade.
    """
    if not crud.level.get(db, grade_in.level_id):
        raise HTTPException(
            status_code=404, detail=LEVEL_DOES_NOT_EXIST,
        )
    grade = crud.grade.get_by_name_and_level(db, name=grade_in.name, level_id=grade_in.level_id)
    if grade and grade.id != grade_id:
        raise HTTPException(
            status_code=409, detail="يوجد صف بنفس هذا الاسم مسبقاً.",
        ) 
    grade = crud.grade.get(db, id=grade_id)

    if not grade:
        raise HTTPException(
            status_code=404, detail=GRADE_DOES_NOT_EXIST,
        )

    grade = crud.grade.update(db, db_obj=grade, obj_in=grade_in)
    return grade


@router.delete('/{grade_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(
    *,
    db: Session = Depends(get_db),
    grade_id: int,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Delete a grade.
    """
    grade = crud.grade.get(db, id=grade_id)

    if not grade:
        raise HTTPException(
            status_code=404,
            detail=GRADE_DOES_NOT_EXIST,
        )
    if grade.subjects:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"لايمكن حذف {grade.name} لانه يوجد مواد مرتبطة بالصف, يجب إلغاء تعيين جميع المواد المرتبطة بالصف ثم حاول مرة اخرى",
        )
    if grade.students:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"لايمكن حذف {grade.name} ,لانه توجد بيانات طلاب مرتبطة بـ هذا الصف, يجب اولاً حذف بيانات الطلاب المرتبطة بـ هذا الصف ثم حاول مرة اخرى.",
        )

    grade = crud.grade.remove(db, payload=grade_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
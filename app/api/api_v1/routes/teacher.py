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

from sqlalchemy.orm import Session
from app.api.deps import CommonQueryParams, get_db
from app.api import deps
from app import (
    crud,
    schemas,
    models
)
router = APIRouter(prefix='/teachers', tags=['Teachers', 'Users'])


@router.post('/assign',  response_model=schemas.AssignedTeacherInDB, status_code=201)
def assign_teacher(
    *,
    db: Session = Depends(get_db),
    body: schemas.AssignedTeacherCreateRequest,
    admin_user = Depends(deps.get_current_active_superuser),
):
    current_school_year = crud.school_year.get_current_school_year(db)
    if not current_school_year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="خطاء يجب عليك إنشاء عام دراسي قبل تخصيص مدرس للمادة"
        )
    is_already_assigned = crud.assigned_teacher.get(
        db, grade_id=body.grade_id, 
        subject_id=body.subject_id, 
        school_year_id=current_school_year.id
    )
    if is_already_assigned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="يبدو ان البيانات التي ارسلتها موجودة مسبقاً في النظام."
        )
    create_schema = schemas.AssignedTeacherCreateInDB(
        **body.dict(),
        school_year_id=current_school_year.id
    )
    return crud.assigned_teacher.create(db, obj_in=create_schema, has_id=False)
    

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

class TeacherSubjectList(Teacher):
    subject: Subject

    class Config:
        orm_mode = True

@router.get('/subjects', response_model=List[TeacherSubjectList], response_model_by_alias=False)
def get_teacher_subjects(
    *, 
    db:Session = Depends(get_db),
    teacher_id: Optional[int],
    grade_id: int ,
    current_teacher = Depends(deps.get_current_active_teacher),
):
    current_school_year = crud.school_year.get_current_school_year(db)
    if not current_school_year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="يبدو انه لايوجد عام دراسي نشط مسجل في النظام."
        )
    grade = crud.grade.get(db, grade_id)
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الصف الذي ارسلته غير موجود في النظام."
        ) 
    
    teacher = crud.user.get(db, teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المعرف الخاص بالمدرس الذي ارسلته غير موجود في النظام."
        )
    
    return db.query(
        models.AssignedTeacher
    ).filter(
        models.AssignedTeacher.teacher_id==teacher_id,
        models.AssignedTeacher.grade_id==grade_id,
        models.AssignedTeacher.school_year_id == current_school_year.id
    ).all()

# @router.get('/{teacher_id}', response_model=schemas.UserInDB)
# def get_teacher(
#     *,
#     db: Session = Depends(get_db),
#     teacher_id: int,
# ):
#     teacher = crud.user.get(db, teacher_id)

#     if not teacher:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"User with id {teacher_id} does not exist."
#         )
#     return teacher


# @router.post('', response_model=schemas.UserInDB, status_code=status.HTTP_201_CREATED)
# def create_teacher(
#     *,
#     db: Session = Depends(get_db),
#     teacher_in: schemas.UserCreate
# ):
#     if not crud.nationality.get(db, teacher_in.nationality_id):
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Nationality with id {teacher_in.nationality_id} not found."
#         )
#     teacher = crud.user.get_by_username(db, username=teacher_in.username)
#     if teacher:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=f"موجود بالفعل في النظام {teacher_in.username} اسم المستخدم",
#         )
#     teacher = crud.user.create_teacher(db, obj_in=teacher_in)
#     return teacher


# @router.put('/{teacher_id}', response_model=schemas.UserInDB)
# def update_teacher(
#     *,
#     db: Session = Depends(get_db),
#     teacher_id: int,
#     teacher_in: schemas.UserUpdate
# ):
#     updated_teacher = crud.user.get(db, teacher_id)

#     if not updated_teacher:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"User with id {teacher_id} does not exist."
#         )

#     teacher = crud.user.get_by_username(db, username=teacher_in.username)
#     if teacher and teacher.id != teacher_id:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=f"موجود بالفعل في النظام {teacher_in.username} اسم المستخدم",
#         )
    
#     if not crud.nationality.get(db, teacher_in.nationality_id):
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Nationality with id {teacher_in.nationality_id} not found."
#         )
    
#     teacher = crud.user.update(db, db_obj=updated_teacher, obj_in=teacher_in)

#     return teacher


# @router.delete('/{teacher_id}', status_code=status.HTTP_204_NO_CONTENT)
# def delete_teacher(
#     *,
#     db: Session = Depends(get_db),
#     teacher_id: int
# ):
#     teacher = crud.user.get(db, teacher_id)

#     if not teacher:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"User with id {teacher_id} does not exist."
#         )

#     if teacher.registrations:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail=f"Cannot delete this teacher because, it has data depends on it."
#         )
#     # check if teacher has no marks then delete it

#     crud.user.remove(db, id=teacher_id)

#     return Response(status_code=status.HTTP_204_NO_CONTENT)

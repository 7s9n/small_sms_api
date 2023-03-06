from typing import (
    List,
    Union,
    Any,
    Optional,
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
    Body
)
from sqlalchemy.orm import Session
# from app.api.deps import CommonQueryParams, get_db
from app.api import deps
from app import models
from app import (
    crud,
    schemas,
)
from app.core.security import verify_password
from app.resources import strings
from app.resources.strings import (
    THERE_IS_DEPENDENT_DATA_ERROR
)
router = APIRouter(prefix='/users', tags=['Users'])

@router.get("/", response_model=Union[schemas.UserPaginatedResponse, List[schemas.UserInDBase]])
def read_users(
    db: Session = Depends(deps.get_db),
    queryParam: deps.CommonQueryParams = Depends(),
    user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Retrieve users.
    """
    if queryParam.page is None or queryParam.limit is None:
        return crud.user.get_all_teachers(db=db)
    
    # if is_superuser is None:
    #     roles = ['a', 't']
    # elif is_superuser:
    #     roles = ['a']
    # else:
    #     roles = ['t']

    users, num_of_rows = crud.user.get_paginated_users(
        db=db, page=queryParam.page, limit=queryParam.limit,
        search=queryParam.search,
        roles=['t']
    )
    if not users:
        return []
    return schemas.UserPaginatedResponse(
        data=users,
        pagination={
            "current_page": queryParam.page,
            "per_page": queryParam.limit,
            "total_records": num_of_rows,
        }
    )

@router.post("/", response_model=schemas.UserInDBase, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Create new user.
    """
    nationality = crud.nationality.get(db, user_in.nationality_id)
    if not nationality:
        raise HTTPException(
            status_code=404,
            detail=strings.NATIONALITY_DOES_NOT_EXIST,
        )

    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=strings.DUBLICATE_USER_NAME,
        )
    
    user = crud.user.create_teacher(db, obj_in=user_in)
    return user

@router.get("/me", response_model=schemas.UserInDBase)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    
    
    return current_user


@router.put("/me", response_model=schemas.UserInDBase)
def update_user_me_password(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    payload: schemas.UserChangePassword,
) -> Any:
    """
    Get current user.
    """
    if not verify_password(payload.old_password, current_user.password):
        raise HTTPException(
            status_code=400,
            detail=strings.OLD_PASSWORD_DOES_NOT_MATCH_DB_STORED_PASSWORD
        )
    user = crud.user.change_password(db, current_user, payload)
    return current_user


@router.put("/{user_id}", response_model=schemas.UserInDBase)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """

    nationality = crud.nationality.get(db, user_in.nationality_id)
    if not nationality:
        raise HTTPException(
            status_code=404,
            detail="الجنسية التي تحمل هذا المعرف غير موجودة.",
        )

    user = crud.user.get_by_username(db, username=user_in.username)
    if user and user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"موجود بالفعل في النظام {user.username} اسم المستخدم",
        )
    
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="المستخدم الذي يحمل هذا المعرف غير موجود",
        )
    
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.get('/{user_id}', response_model=schemas.UserInDBase)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
)-> Any:
    pass
    user = crud.user.get(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"المستخدم غير موجود."
        )
    return user

@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
)-> Any:
    user = crud.user.get(db, user_id)

    if not user or user.role != 't':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="لايوجد مدرس يطابق البيانات التي ادخلتها."
        )
    if user.teacher_assigned_grades_and_subjects:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=THERE_IS_DEPENDENT_DATA_ERROR,
        )

    crud.user.remove(db, payload=user_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# def assign_teacher():
#     pass
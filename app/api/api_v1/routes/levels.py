from typing import (
    List,
    Union,
)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from sqlalchemy.orm import Session
from app.api import deps
from app.api.deps import get_db, CommonQueryParams
from app import (
    crud,
    schemas,
    models,
)
router = APIRouter(prefix='/levels', tags=['Levels'])


@router.get('', response_model=Union[schemas.LevelsResponseModel, List[schemas.LevelInDB]])
def get_levels(
    *,
    db: Session = Depends(get_db),
    queryParam: CommonQueryParams = Depends(),
    user: models.User = Depends(deps.get_current_active_user)
):
    """
    Retrieve all Levels.
    """
    
    if queryParam.page is None or queryParam.limit is None:
        return crud.level.get_multi(db=db)

    num_of_rows, levels = crud.level.get_multi_paginated(
        db, page=queryParam.page, limit=queryParam.limit,
        filters={"name": queryParam.search}
    )
    if not levels:
        return []
    return schemas.LevelsResponseModel(
        data=levels,
        pagination= {
            "current_page": queryParam.page,
            "per_page": queryParam.limit,
            "total_records": num_of_rows,
        }
    )


@router.get('/{level_id}', response_model=schemas.LevelInDB)
def get_level(
    *,
    db: Session = Depends(get_db),
    level_id: int,
    user: models.User = Depends(deps.get_current_active_user)
):
    """
    Retrieve one level based on id key.
    """
    level = crud.level.get(db, id=level_id)

    if not level:
        raise HTTPException(
            status_code=404, detail=f"المرحلة الذي تبحث عنها غير موجودة",
        )

    return level


@router.post('', response_model=schemas.LevelInDB, status_code=status.HTTP_201_CREATED)
def create_level(
    *,
    db: Session = Depends(get_db),
    level_in: schemas.LevelCreate,
    user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    Create a level.
    """
    level = crud.level.get_by_name(db, name=level_in.name)

    if level:
        raise HTTPException(
            status_code=409, detail=f"يوجد مرحلة دراسية  بهذا الاسم ({level_in.name}) بالفعل",
        )
    level = crud.level.create(db, obj_in=level_in)
    return level


@router.put('/{level_id}', response_model=schemas.LevelInDB)
def update_level(
    *,
    db: Session = Depends(get_db),
    level_id: int,
    level_in: schemas.LevelUpdate,
    user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    Update a level.
    """
    level = crud.level.get_by_name(db, name=level_in.name)

    if level and level.id != level_id:
        raise HTTPException(
            status_code=409, detail=f"يوجد مرحلة دراسية  بهذا الاسم ({level_in.name}) بالفعل",
        )

    level = crud.level.get(db, id=level_id)

    if not level:
        raise HTTPException(
            status_code=404, detail=f"لاتوجد مرحلة دراسية",
        )

    level = crud.level.update(db, db_obj=level, obj_in=level_in)
    return level


@router.delete('/{level_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_level(
    *,
    db: Session = Depends(get_db),
    level_id: int,
    user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    Delete a level.
    """
    level = crud.level.get(db, id=level_id)
    if not level:
        raise HTTPException(
            status_code=404, detail=f"المرحلة رقم {level_id} غير موجودة",
        )
    if level.grades:
        raise HTTPException(
            status_code=409, detail=f"لايمكن حذف هذه المرحلة لانها مرتبطة بفصول.",
        )
    level = crud.level.remove(db, payload=level_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

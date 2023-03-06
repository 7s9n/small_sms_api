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
    models
)
router = APIRouter(prefix='/grading-scales', tags=['Grading Scale'])


@router.get('', response_model=Union[schemas.GradingScalesResponseModel, List[schemas.GradingScaleInDB]])
def get_grading_scales(
    *,
    db: Session = Depends(get_db),
    queryParam: CommonQueryParams = Depends(),
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Retrieve all Grading Scales.
    """
    if queryParam.page is None or queryParam.limit is None:
        return crud.grading_scale.get_multi(db=db)

    num_of_rows, grading_scales = crud.grading_scale.get_multi_paginated(
        db, page=queryParam.page, limit=queryParam.limit,
        filters={"name": queryParam.search}
    )
    return schemas.GradingScalesResponseModel(
        data=grading_scales,
        pagination={
            "current_page": queryParam.page,
            "per_page": queryParam.limit,
            "total_records": num_of_rows,
        }
    )


@router.get('/{grading_scale_id}', response_model=schemas.GradingScaleInDB)
def get_grading_scale(
    *,
    db: Session = Depends(get_db),
    grading_scale_id: int,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Retrieve one grading scale based on id key.
    """
    grading_scale = crud.grading_scale.get(db, id=grading_scale_id)

    if not grading_scale:
        raise HTTPException(
            status_code=404, detail=f"التقدير الذي تبحث عنه غير موجود",
        )
    return grading_scale


@router.post('', response_model=schemas.GradingScaleInDB, status_code=status.HTTP_201_CREATED)
def create_grading_scale(
    *,
    db: Session = Depends(get_db),
    grading_scale_in: schemas.GradingScaleCreate,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Create a grading scale.
    """
    grading_scale = crud.grading_scale.get_by_name(
        db, name=grading_scale_in.name)

    if grading_scale:
        raise HTTPException(
            status_code=409, detail=f"يوحد تقدير بنفس هذا الأسم {grading_scale_in.name}.",
        )
    grading_scale = crud.grading_scale.get_by_percentage(
        db, lowest_percentage=grading_scale_in.lowest_percentage, highest_percentage=grading_scale_in.highest_percentage)
    
    if grading_scale:
        raise HTTPException(
            status_code=409, detail=f"يوجد تقدير بنفس النسب التي ادخلتها.",
        )

    grading_scale = crud.grading_scale.create(db, obj_in=grading_scale_in)
    return grading_scale


@router.put('/{grading_scale_id}', response_model=schemas.GradingScaleInDB)
def update_grading_scale(
    *,
    db: Session = Depends(get_db),
    grading_scale_id: int,
    grading_scale_in: schemas.GradingScaleUpdate,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Update a grading scale.
    """
    grading_scale = crud.grading_scale.get(db, id=grading_scale_id)

    if not grading_scale:
        raise HTTPException(
            status_code=404, detail=f"لايوجد تقدير بالمعرف الذي ادخلته",
        )

    grading_scale = crud.grading_scale.get_by_name(
        db, name=grading_scale_in.name)

    if grading_scale and grading_scale.id != grading_scale_id:
        raise HTTPException(
            status_code=409, detail=f"يوحد تقدير بنفس هذا الأسم {grading_scale_in.name}.",
        )

    grading_scale = crud.grading_scale.get_by_percentage(
        db, lowest_percentage=grading_scale_in.lowest_percentage, highest_percentage=grading_scale_in.highest_percentage)
    
    if grading_scale and grading_scale.id != grading_scale_id:
        raise HTTPException(
            status_code=409, detail=f"يوجد تقدير بنفس النسب التي ادخلتها.",
        )

    grading_scale = crud.grading_scale.update(
        db, db_obj=grading_scale, obj_in=grading_scale_in)
    return grading_scale


@router.delete('/{grading_scale_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_grading_scale(
    *,
    db: Session = Depends(get_db),
    grading_scale_id: int,
    user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Delete a grading scale.
    """
    grading_scale = crud.grading_scale.get(db, id=grading_scale_id)
    if not grading_scale:
        raise HTTPException(
            status_code=404, detail=f"لايوجد تقدير بالمعرف الذي ادخلته",
        )
    # check if grading scale connected whith scores

    grading_scale = crud.grading_scale.remove(db, id=grading_scale_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from typing import (
    Generic,
    Type,
    TypeVar,
    List,
    Dict,
    Any,
    Union,
    Optional,
    Tuple
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc, func, literal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.base import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    # def get_multi_paginated(
    #     self, db: Session, *, page: int = 0, limit: int = 20, search: str = "",filters: Dict[str, Any], params: Dict[str, Any] = None
    # ) -> List[ModelType]:
    #     query = db.query(self.model)
    #     if params:
    #         for attr in [x for x in params if params[x] is not None]:
    #             query = query.filter(getattr(self.model, attr) == params[attr])
        
    #     if filters:
    #         for k, v in filters.items(): 
    #             query = db.query(self.model).filter(getattr(self.model, k).like(literal(f"%{v}%")))

    #     return query.order_by(desc(self.model.id)).offset((page - 1) * limit).limit(limit).all()

    def get_multi_paginated(
        self, db: Session, *, page: int = 0, limit: int = 20, search: str = "",filters: Dict[str, Any] = None, params: Dict[str, Any] = None, sort_by="id"
    ) -> Tuple:
        query = db.query(self.model)
        if params:
            for attr in [x for x in params if params[x] is not None]:
                query = query.filter(getattr(self.model, attr) == params[attr])
        
        if filters:
            for k, v in filters.items(): 
                query = query.filter(getattr(self.model, k).like(literal(f"%{v}%")))
        
        number_of_rows = query.count()
        rows = query.order_by(desc(getattr(self.model,sort_by))).offset((page - 1) * limit).limit(limit).all()
        return (number_of_rows, rows)
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 20, params: Dict[str, Any] = None,
        sort_by: str = None
    ) -> List[ModelType]:
        query = db.query(self.model)
        if params:
            for attr in [x for x in params if params[x] is not None]:
                query = query.filter(getattr(self.model, attr) == params[attr])
        # return query.offset(skip).limit(limit).all()
        if sort_by:
            query.order_by(getattr(self.model,sort_by))
        return query.all()

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_pk(self, db: Session, pk: Union[int, Tuple]) -> Optional[ModelType]:
        return db.query(self.model).get(pk)

    def get_by_custom_filters(self, db: Session, filters: Dict[str, Any]):
        query = db.query(self.model)
        if filters:
            for attr in [x for x in filters if filters[x] is not None]:
                query = query.filter(getattr(self.model, attr) == filters[attr])
        return query.first()

    def create(self, db: Session, *, obj_in: CreateSchemaType, has_id=True) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        if has_id:
            max_id = db.query(func.max(self.model.id)).scalar()
            max_id = 1 if max_id is None else max_id + 1
            db_obj = self.model(id=max_id, **obj_in_data)
        else:
            db_obj = self.model(**obj_in_data)
        # db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, payload) -> ModelType:
        obj = db.query(self.model).get(payload)
        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session):
        return db.query(self.model).count()

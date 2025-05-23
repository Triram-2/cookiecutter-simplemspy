# src/db/base_repository.py
"""
Модуль с базовым классом репозитория для CRUD-операций.
"""

import warnings
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, delete, func, exc as sa_exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import Base # Импортируем нашу декларативную базу

ModelType = TypeVar("ModelType", bound=Base) 
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый репозиторий с CRUD-операциями для моделей SQLAlchemy.

    Атрибуты:
        model (Type[ModelType]): Класс модели SQLAlchemy.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Инициализатор репозитория.

        Args:
            model: Класс модели SQLAlchemy.
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Получение одной записи по её ID.

        Args:
            db: Асинхронная сессия SQLAlchemy.
            id: ID записи.

        Returns:
            Экземпляр модели или None, если не найдено.
        """
        statement = select(self.model).where(self.model.id == id) # type: ignore
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Получение списка записей с возможностью пагинации.

        Args:
            db: Асинхронная сессия SQLAlchemy.
            skip: Количество записей для пропуска.
            limit: Максимальное количество записей для возврата.

        Returns:
            Список экземпляров модели.
        """
        statement = select(self.model).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())
    
    async def get_all(self, db: AsyncSession) -> List[ModelType]:
        """
        Получение всех записей из таблицы.

        Args:
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Список всех экземпляров модели.
        """
        statement = select(self.model)
        result = await db.execute(statement)
        return list(result.scalars().all())

    async def count(self, db: AsyncSession) -> int:
        """
        Получение общего количества записей в таблице.

        Args:
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Количество записей.
        """
        statement = select(func.count()).select_from(self.model)
        result = await db.execute(statement)
        return result.scalar_one()


    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Создание новой записи.

        Args:
            db: Асинхронная сессия SQLAlchemy.
            obj_in: Pydantic схема с данными для создания.

        Returns:
            Созданный экземпляр модели.
        """
        obj_in_data = jsonable_encoder(obj_in, exclude_unset=True)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        try:
            await db.commit()
        except sa_exc.IntegrityError as e:
            await db.rollback()
            warnings.warn(f"IntegrityError during create: {e}", RuntimeWarning)
            raise e
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Обновление существующей записи.

        Args:
            db: Асинхронная сессия SQLAlchemy.
            db_obj: Экземпляр модели для обновления.
            obj_in: Pydantic схема или словарь с данными для обновления.

        Returns:
            Обновленный экземпляр модели.
        """
        obj_data = jsonable_encoder(db_obj) 
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True) 
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        try:
            await db.commit()
        except sa_exc.IntegrityError as e:
            await db.rollback()
            warnings.warn(f"IntegrityError during update: {e}", RuntimeWarning)
            raise e
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """
        Удаление записи по её ID.

        Args:
            db: Асинхронная сессия SQLAlchemy.
            id: ID записи для удаления.

        Returns:
            Удаленный экземпляр модели или None, если запись не найдена.
        """
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            try:
                await db.commit()
            except sa_exc.IntegrityError as e: # Например, если есть связанные записи, не позволяющие удаление
                await db.rollback()
                warnings.warn(f"IntegrityError during delete: {e}", RuntimeWarning)
                raise e
            return obj
        return None

    async def delete_obj(self, db: AsyncSession, *, db_obj: ModelType) -> ModelType:
        """
        Удаление существующего объекта базы данных.

        Args:
            db: Асинхронная сессия SQLAlchemy.
            db_obj: Экземпляр модели для удаления.

        Returns:
            Удаленный экземпляр модели.
        """
        await db.delete(db_obj)
        try:
            await db.commit()
        except sa_exc.IntegrityError as e:
            await db.rollback()
            warnings.warn(f"IntegrityError during delete_obj: {e}", RuntimeWarning)
            raise e
        return db_obj

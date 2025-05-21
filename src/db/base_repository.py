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

# Определяем дженерик тип для модели SQLAlchemy
ModelType = TypeVar("ModelType", bound=Base) 
# Определяем дженерик тип для Pydantic схемы создания
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# Определяем дженерик тип для Pydantic схемы обновления
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
        # Преобразуем Pydantic модель в словарь, исключая неустановленные значения
        obj_in_data = jsonable_encoder(obj_in, exclude_unset=True)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        try:
            await db.commit()
        except sa_exc.IntegrityError as e:
            await db.rollback()
            # Можно здесь добавить логирование или специфическую обработку ошибки
            warnings.warn(f"IntegrityError during create: {e}", RuntimeWarning)
            raise e # Перевыбрасываем ошибку, чтобы ее можно было обработать выше
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
        obj_data = jsonable_encoder(db_obj) # Получаем текущие данные объекта как словарь
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # Используем exclude_unset=True, чтобы обновлять только переданные поля
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
        return None # Или можно вызывать исключение, если объект не найден

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

# Пример использования (потребует определения User, UserCreate, UserUpdate):
# from pydantic import BaseModel
# class User(Base, TimestampMixin): # Предполагается, что User определен в base.py или models.py
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String)

# class UserCreate(BaseModel):
#     name: str

# class UserUpdate(BaseModel):
#     name: Optional[str] = None

# user_repo = BaseRepository[User, UserCreate, UserUpdate](User)

# async def example_usage(db_session: AsyncSession):
#     new_user_data = UserCreate(name="John Doe")
#     user = await user_repo.create(db_session, obj_in=new_user_data)
#     print(f"Created user: {user.id}, {user.name}")
#     retrieved_user = await user_repo.get(db_session, id=user.id)
#     if retrieved_user:
#         updated_user_data = UserUpdate(name="Johnathan Doe")
#         await user_repo.update(db_session, db_obj=retrieved_user, obj_in=updated_user_data)
#     all_users = await user_repo.get_all(db_session)
#     for u in all_users:
#         await user_repo.delete(db_session, id=u.id)

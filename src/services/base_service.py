# src/services/base_service.py
"""
Модуль с базовым классом сервиса для CRUD-операций.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import Base as BaseModelDB  # SQLAlchemy Base Model
from src.db.base_repository import BaseRepository  # Наш базовый репозиторий

# Дженерик типы для моделей и схем
ModelType = TypeVar("ModelType", bound=BaseModelDB)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
# Дженерик тип для репозитория, конкретизирующий типы для BaseRepository
RepositoryType = TypeVar(
    "RepositoryType",
    bound=BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType],
)


class BaseService(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, RepositoryType]
):
    """
    Базовый сервис с CRUD-операциями.

    Атрибуты:
        repository (RepositoryType): Экземпляр репозитория для работы с данными.
    """

    def __init__(self, repository: RepositoryType):
        """
        Инициализатор сервиса.

        Args:
            repository: Экземпляр репозитория.
        """
        self.repository = repository

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Получение одной записи по её ID.

        Args:
            db: Асинхронная сессия SQLAlchemy.
            id: ID записи.

        Returns:
            Экземпляр модели или None, если не найдено.
        """
        return await self.repository.get(db, id=id)

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
        return await self.repository.get_multi(db, skip=skip, limit=limit)

    async def get_all(self, db: AsyncSession) -> List[ModelType]:
        """
        Получение всех записей.

        Args:
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Список всех экземпляров модели.
        """
        return await self.repository.get_all(db)

    async def count(self, db: AsyncSession) -> int:
        """
        Получение общего количества записей.

        Args:
            db: Асинхронная сессия SQLAlchemy.

        Returns:
            Количество записей.
        """
        return await self.repository.count(db)

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Создание новой записи.
        В более сложных случаях здесь может быть дополнительная бизнес-логика
        до или после вызова репозитория.

        Args:
            db: Асинхронная сессия SQLAlchemy.
            obj_in: Pydantic схема с данными для создания.

        Returns:
            Созданный экземпляр модели.
        """
        # Тут может быть какая-то бизнес-логика до создания объекта
        # Например, проверка прав, генерация дополнительных полей и т.д.
        db_obj = await self.repository.create(db, obj_in=obj_in)
        # И/или после создания (например, отправка уведомления)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        id: Any,  # Сервис обычно оперирует ID, а не db_obj напрямую
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> Optional[ModelType]:
        """
        Обновление существующей записи по ID.
        В более сложных случаях здесь может быть дополнительная бизнес-логика.

        Args:
            db: Асинхронная сессия SQLAlchemy.
            id: ID обновляемого объекта.
            obj_in: Pydantic схема или словарь с данными для обновления.

        Returns:
            Обновленный экземпляр модели или None, если объект не найден.
        """
        db_obj = await self.repository.get(db, id=id)
        if not db_obj:
            return None  # Или можно вызывать исключение (например, HTTPException(404))

        # Дополнительная бизнес-логика до обновления
        updated_db_obj = await self.repository.update(db, db_obj=db_obj, obj_in=obj_in)
        # И/или после обновления
        return updated_db_obj

    async def delete(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        """
        Удаление записи по её ID.
        В более сложных случаях здесь может быть дополнительная бизнес-логика.

        Args:
            db: Асинхронная сессия SQLAlchemy.
            id: ID записи для удаления.

        Returns:
            Удаленный экземпляр модели или None, если запись не найдена.
        """
        # Дополнительная бизнес-логика до удаления (проверка прав, связанных сущностей и т.д.)
        deleted_obj = await self.repository.delete(db, id=id)
        # И/или после удаления (например, очистка связанных данных, если это не делается на уровне БД)
        if not deleted_obj:
            return None  # Или HTTPException(404)
        return deleted_obj


# Пример использования (потребует определения соответствующих моделей, схем и репозитория):
#
# from sqlalchemy.orm import Mapped, mapped_column # Для примера UserModel
# class UserModel(BaseModelDB): # Пример модели SQLAlchemy
#     __tablename__ = "users"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column()

# class UserCreateSchema(BaseModel): # Схема Pydantic для создания
#     name: str

# class UserUpdateSchema(BaseModel): # Схема Pydantic для обновления
#     name: Optional[str] = None

# class UserRepository(BaseRepository[UserModel, UserCreateSchema, UserUpdateSchema]):
#     def __init__(self):
#         super().__init__(UserModel)

# class UserService(BaseService[UserModel, UserCreateSchema, UserUpdateSchema, UserRepository]):
#     def __init__(self, repository: UserRepository):
#         super().__init__(repository)

# # Использование в коде:
# # from src.db import get_async_session # Для примера использования
# # user_repo = UserRepository()
# # user_service = UserService(user_repo)
# # async def main_example():
# #     async with get_async_session() as session:
# #         new_user_data = UserCreateSchema(name="John")
# #         # Убедитесь, что UserModel, UserCreateSchema, UserUpdateSchema, UserRepository определены
# #         # и база данных (включая таблицу users) существует и доступна.
# #         # new_user = await user_service.create(session, obj_in=new_user_data)
# #         # print(f"Created user: {new_user.name if new_user else 'Error'}")
# #         # if new_user:
# #         #     user_in_db = await user_service.get(session, id=new_user.id)
# #         #     print(f"Fetched user: {user_in_db.name if user_in_db else 'Not found'}")
# # asyncio.run(main_example()) # Пример запуска асинхронной функции (требует импорта asyncio)

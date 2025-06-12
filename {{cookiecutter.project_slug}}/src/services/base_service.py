from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from my_awesome_project.db.base_repository import BaseRepository

ModelType = TypeVar("ModelType", bound=Any)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    repository: BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]

    def __init__(
        self, repository: BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]
    ):
        self.repository = repository

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        return await self.repository.get(db, id=id)

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return await self.repository.get_multi(db, skip=skip, limit=limit)

    async def get_all(self, db: AsyncSession) -> List[ModelType]:
        return await self.repository.get_all(db)

    async def count(self, db: AsyncSession) -> int:
        return await self.repository.count(db)

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = await self.repository.create(db, obj_in=obj_in)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        id: Any,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> Optional[ModelType]:
        db_obj = await self.repository.get(db, id=id)
        if not db_obj:
            return None
        updated_db_obj = await self.repository.update(db, db_obj=db_obj, obj_in=obj_in)
        return updated_db_obj

    async def delete(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        deleted_obj = await self.repository.delete(db, id=id)
        if not deleted_obj:
            return None
        return deleted_obj

# src/schemas/common.py
"""
Общие Pydantic схемы, используемые в приложении.
"""

from datetime import datetime
from typing import Generic, List, TypeVar, Any, ClassVar, Dict

from pydantic import BaseModel, Field, conint

# Для обобщенных типов в PaginatedResponse
T = TypeVar("T")


class Msg(BaseModel):
    """
    Схема для простых текстовых сообщений API.
    """

    message: str = Field(..., description="Текстовое сообщение от API")

    class Config:
        # Добавляем пример для OpenAPI документации
        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {"message": "Действие успешно выполнено"}
        }


class IDModel(BaseModel):
    """
    Базовая схема для моделей, имеющих целочисленный ID.
    """

    id: int = Field(..., description="Уникальный идентификатор", example=1) # type: ignore[reportUnknownVariableType, reportCallIssue]


class TimestampModel(BaseModel):
    """
    Базовая схема (или миксин) для моделей с временными метками.
    """

    created_at: datetime = Field(
        ..., description="Время создания записи", example="2023-10-26T10:00:00Z"
    )
    updated_at: datetime = Field(
        ...,
        description="Время последнего обновления записи",
        example="2023-10-26T12:00:00Z",
    )

    class Config:
        # Позволяет Pydantic корректно работать с объектами ORM,
        # обращаясь к атрибутам через model.attr вместо model['attr']
        from_attributes = True


class PaginationParams(BaseModel):
    """
    Параметры для пагинации в запросах API.
    """

    skip: conint(ge=0) = Field(
        0, description="Количество пропускаемых записей (смещение)"
    )  # type: ignore
    limit: conint(ge=1, le=200) = Field(
        100, description="Максимальное количество записей на странице (до 200)"
    )  # type: ignore


class PaginatedResponse(Generic[T], BaseModel):
    """
    Обобщенная схема для пагинированных ответов API.
    """

    items: List[T] = Field(..., description="Список элементов на текущей странице")
    total: int = Field(..., description="Общее количество элементов", example=100)
    skip: int = Field(..., description="Количество пропущенных элементов", example=0)
    limit: int = Field(..., description="Количество элементов на странице", example=10)

    class Config:
        "Пример для OpenAPI (может потребовать доработки в зависимости от типа T)"

        json_schema_extra: ClassVar[Dict[str, Any]] = {
            "example": {
                "items": [
                    {"id": 1, "name": "Пример объекта 1"},
                    {"id": 2, "name": "Пример объекта 2"},
                ],
                "total": 2,
                "skip": 0,
                "limit": 10,
            }
        }


# Пример использования IDModel и TimestampModel вместе:
# class MyItemBase(TimestampModel, IDModel): # Порядок важен, если есть коллизии полей Config
#     pass

# class MyItem(MyItemBase):
#     name: str
#     description: Optional[str] = None

#     class Config:
#         from_attributes = True # Для корректной работы с ORM моделями
#         json_schema_extra = {
#             "example": {
#                 "id": 1,
#                 "name": "Пример элемента",
#                 "description": "Это пример элемента с временными метками.",
#                 "created_at": "2023-01-01T12:00:00Z",
#                 "updated_at": "2023-01-01T13:00:00Z",
#             }
#         }

# src/schemas/common.py
"""
Общие Pydantic схемы, используемые в приложении.
"""

from datetime import datetime
from typing import Generic, List, TypeVar, Any, ClassVar, Dict

from pydantic import BaseModel, Field

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

    id: int = Field(..., description="Уникальный идентификатор", example=1)  # type: ignore[reportUnknownVariableType, reportCallIssue]


class TimestampModel(BaseModel):
    """
    Базовая схема (или миксин) для моделей с временными метками.
    """

    created_at: datetime
    updated_at: datetime

    class Config:
        # Позволяет Pydantic корректно работать с объектами ORM,
        # обращаясь к атрибутам через model.attr вместо model['attr']
        from_attributes = True


class PaginationParams(BaseModel):
    """
    Параметры для пагинации в запросах API.
    """

    skip: int = Field(
        default=0, ge=0, description="Количество пропускаемых записей (смещение)"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=200,
        description="Максимальное количество записей на странице (до 200)",
    )


class PaginatedResponse(Generic[T], BaseModel):
    """
    Обобщенная схема для пагинированных ответов API.
    """

    items: List[T] = Field(..., description="Список элементов на текущей странице")
    total: int = Field(..., description="Общее количество элементов", example=100)  # type: ignore[reportUnknownVariableType, reportCallIssue, reportInvalidTypeForm]
    skip: int = Field(..., description="Количество пропущенных элементов", example=0)  # type: ignore[reportUnknownVariableType, reportCallIssue]
    limit: int = Field(..., description="Количество элементов на странице", example=10)  # type: ignore[reportUnknownVariableType, reportCallIssue]

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

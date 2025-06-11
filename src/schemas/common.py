# src/schemas/common.py
"""
Общие Pydantic схемы, используемые в приложении.
"""

from datetime import datetime
from typing import Generic, List, TypeVar, ClassVar  # Added ClassVar back

from pydantic import BaseModel, Field, ConfigDict  # Added ConfigDict

# Для обобщенных типов в PaginatedResponse
T = TypeVar("T")


class Msg(BaseModel):
    """
    Схема для простых текстовых сообщений API.
    """

    message: str = Field(..., description="Текстовое сообщение от API")

    model_config: ClassVar[ConfigDict] = {
        "json_schema_extra": {"example": {"message": "Действие успешно выполнено"}}
    }


class IDModel(BaseModel):
    """
    Базовая схема для моделей, имеющих целочисленный ID.
    """

    id: int = Field(
        ...,
        description="Уникальный идентификатор",
        json_schema_extra={"example": 1},  # Changed from example=1
    )  # type: ignore[reportUnknownVariableType, reportCallIssue]


class TimestampModel(BaseModel):
    """
    Базовая схема (или миксин) для моделей с временными метками.
    """

    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = {
        # Позволяет Pydantic корректно работать с объектами ORM,
        # обращаясь к атрибутам через model.attr вместо model['attr']
        "from_attributes": True
    }


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


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Обобщенная схема для пагинированных ответов API.
    """

    items: List[T] = Field(..., description="Список элементов на текущей странице")
    total: int = Field(
        ...,
        description="Общее количество элементов",
        json_schema_extra={"example": 100},  # Changed from example=100
    )  # type: ignore[reportUnknownVariableType, reportCallIssue, reportInvalidTypeForm]
    skip: int = Field(
        ...,
        description="Количество пропущенных элементов",
        json_schema_extra={"example": 0},  # Changed from example=0
    )  # type: ignore[reportUnknownVariableType, reportCallIssue]
    limit: int = Field(
        ...,
        description="Количество элементов на странице",
        json_schema_extra={"example": 10},  # Changed from example=10
    )  # type: ignore[reportUnknownVariableType, reportCallIssue]

    model_config: ClassVar[ConfigDict] = {
        "json_schema_extra": {
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
        # Note: The comment "Пример для OpenAPI (может потребовать доработки в зависимости от типа T)"
        # was part of the Config class docstring. It's not directly translatable to ConfigDict
        # unless it's a general comment about the model itself.
    }


# Пример использования IDModel и TimestampModel вместе:
# class MyItemBase(TimestampModel, IDModel): # Порядок важен, если есть коллизии полей Config
#     pass

# class MyItem(MyItemBase):
#     name: str
#     description: Optional[str] = None

#     model_config: ConfigDict = { # Example of how it would look if MyItem was defined here
#         "from_attributes": True, # Для корректной работы с ORM моделями
#         "json_schema_extra": {
#             "example": {
#                 "id": 1,
#                 "name": "Пример элемента",
#                 "description": "Это пример элемента с временными метками.",
#                 "created_at": "2023-01-01T12:00:00Z",
#                 "updated_at": "2023-01-01T13:00:00Z",
#             }
#         }

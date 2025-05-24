# src/schemas/__init__.py
"""
Пакет для Pydantic схем, используемых для валидации данных API,
а также для сериализации и десериализации данных при взаимодействии с базой данных.

Основные рекомендации при создании схем:
1.  **Базовые схемы**: Определите базовую схему для каждой модели, содержащую общие поля.
    Пример: `UserBase`.
2.  **Схемы для создания**: Наследуйтесь от базовой схемы и добавьте поля, необходимые
    только при создании. Пароли или другие чувствительные данные должны быть здесь,
    но не в схемах для чтения.
    Пример: `UserCreate(UserBase)`.
3.  **Схемы для обновления**: Наследуйтесь от базовой схемы, но сделайте все поля
    опциональными, так как при обновлении могут изменяться не все поля.
    Пример: `UserUpdate(UserBase)` (с `Optional` для всех полей).
4.  **Схемы для чтения/ответа API**: Наследуйтесь от базовой схемы (и, возможно,
    `IDModel`, `TimestampModel` из `src.schemas.common`) и добавьте поля, которые
    должны возвращаться клиенту. Исключите чувствительные данные.
    Пример: `UserRead(UserBase, IDModel, TimestampModel)`.
    Установите `Config.from_attributes = True` (или `orm_mode = True` для Pydantic v1)
    для корректной сериализации из объектов SQLAlchemy.

Пример структуры для модели `Item`:

```python
# В файле src/schemas/item_schemas.py (пример)
from typing import Optional
from pydantic import BaseModel, Field
from .common import IDModel, TimestampModel # Импорт общих схем

class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Название товара")
    description: Optional[str] = Field(None, max_length=500, description="Описание товара")

class ItemCreate(ItemBase):
    pass # Нет дополнительных полей при создании в данном простом примере

class ItemUpdate(BaseModel): # Или наследовать от ItemBase и сделать все поля Optional
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ItemRead(ItemBase, IDModel, TimestampModel):
    # Эта схема будет использоваться для ответа API, включая id и временные метки

    class Config:
        from_attributes = True # Для сериализации из ORM-модели Item
        json_schema_extra = {
            "example": {
                "id": 123,
                "title": "Пример товара",
                "description": "Это подробное описание примера товара.",
                "created_at": "2023-01-01T10:00:00Z",
                "updated_at": "2023-01-01T14:30:00Z"
            }
        }
```
"""

from .common import Msg, IDModel, TimestampModel, PaginationParams, PaginatedResponse

__all__ = ["IDModel", "Msg", "PaginatedResponse", "PaginationParams", "TimestampModel"]

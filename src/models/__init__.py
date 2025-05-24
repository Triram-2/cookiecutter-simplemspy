# src/models/__init__.py
"""
Пакет для определения моделей данных SQLAlchemy.

Все модели должны наследоваться от `Base` из `src.db.base`.
Например:

```python
# В файле src/models/my_model.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base, TimestampMixin # Импортируем Base и, возможно, TimestampMixin

class MyModel(Base, TimestampMixin): # TimestampMixin опционален
    __tablename__ = "my_models" # Имя таблицы (автоматически генерируется, если не указано)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, comment="Название модели")
    description: Mapped[str | None] = mapped_column(String, nullable=True, comment="Описание")

    # ... другие поля ...
```

Для того чтобы Alembic мог обнаруживать ваши модели для автоматической генерации миграций,
убедитесь, что они импортированы где-то, где Alembic их "увидит".
Обычно это делается путем импорта всех модулей с моделями (или просто `Base` и всех моделей)
в файл `env.py` вашего окружения Alembic, либо импортируя их в `src.db.base` (менее предпочтительно),
или обеспечив их импорт через другие части приложения, которые доступны Alembic.

Самый простой способ — импортировать все модули из этой директории в этот `__init__.py`,
а затем импортировать сам `src.models` в `env.py`. Например, если у вас есть `my_model.py`:

```python
# В src/models/__init__.py (этот файл)
# from .my_model import MyModel
# __all__ = ["MyModel"]
```
Или же, импортировать модуль целиком:
```python
# В env.py Alembic:
# import src.models.my_model
# или если __all__ настроен в src/models/__init__.py:
# from src.models import *
```

Рекомендуется явно импортировать каждую модель или модуль с моделями в `env.py` Alembic
для лучшего контроля и явности.
"""

# На данный момент здесь нет моделей для экспорта.
# Когда вы добавите свои модели, вы можете либо импортировать их здесь,
# чтобы сделать их доступными как `from src.models import YourModel`,
# либо импортировать их напрямую из их модулей (`from src.models.your_module import YourModel`).

# Пример, если бы у нас была модель User в user.py:
# from .user import User
#
# __all__ = [
#     "User",
# ]

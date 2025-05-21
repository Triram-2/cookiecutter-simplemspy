# src/db/base.py
"""
Основа для всех моделей SQLAlchemy.
Включает декларативную базу и опциональный миксин для временных меток.
"""

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr
from typing import Any
import re

# Декларативная база для всех моделей
# https://alembic.sqlalchemy.org/en/latest/naming.html
# Соглашение об именовании для Alembic, чтобы миграции генерировались корректно
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class _Base:
    """
    Базовый класс для моделей SQLAlchemy с автоматическим именованием таблицы.
    Имя таблицы будет преобразовано из MyModelClass в my_model_class.
    """
    @declared_attr # type: ignore
    def __tablename__(cls) -> str:
        # Преобразует имя класса из CamelCase в snake_case для имени таблицы
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        return name

Base: Any = declarative_base(cls=_Base, metadata=None) # metadata=None для Alembic, он сам подставит


class TimestampMixin:
    """
    Миксин для добавления полей created_at и updated_at в модели.
    `created_at`: время создания записи.
    `updated_at`: время последнего обновления записи.
    """
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, 
        default=func.now(), 
        server_default=func.now(), # Для генерации на стороне БД
        comment="Время создания записи"
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(), # Обновляется при каждом обновлении записи
        server_default=func.now(), # Для генерации на стороне БД
        server_onupdate=func.now(), # Для обновления на стороне БД
        comment="Время последнего обновления записи"
    )

# Пример использования:
# from sqlalchemy import Column, Integer, String
# class MyModel(Base, TimestampMixin):
#     id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
#     name: Mapped[str] = mapped_column(String, index=True)

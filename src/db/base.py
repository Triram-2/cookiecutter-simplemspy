# src/db/base.py
"""
Основа для всех моделей SQLAlchemy.
Включает декларативную базу и опциональный миксин для временных меток.
"""

import re
from datetime import datetime  # Import datetime for Mapped[datetime]
from typing import Any, Dict, Type  # Import necessary typing modules

from sqlalchemy import DateTime, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr

# Декларативная база для всех моделей
# https://alembic.sqlalchemy.org/en/latest/naming.html
# Соглашение об именовании для Alembic, чтобы миграции генерировались корректно
convention: Dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# If metadata were to be defined explicitly with convention (Alembic usually handles this)
# metadata_obj: MetaData = MetaData(naming_convention=convention)


class _Base:
    """
    Базовый класс для моделей SQLAlchemy с автоматическим именованием таблицы.
    Имя таблицы будет преобразовано из MyModelClass в my_model_class.
    """

    # This id could be part of PkModel as per task, but often included in a general base
    # id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)

    @declared_attr
    def __tablename__(cls: Type[Any]) -> str:  # cls is a type, e.g., MyModel
        # Преобразует имя класса из CamelCase в snake_case для имени таблицы
        # The noqa: N805 for 'cls' might still be needed depending on linter rules for @declared_attr
        name: str = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        return name


# The result of declarative_base() is a metaclass instance (usually DeclarativeMeta)
# which is then used as a base class for models.
# So, `Base` is a type (a class). `Type[Any]` is a general way to type a class.
# `DeclarativeMeta` is also accurate for the type of `Base` itself.
# For practical purposes, often `Any` is used if type checkers struggle,
# but `Type[Any]` or `type` is more precise for the variable holding the base class.
# Let's use `DeclarativeMeta` as it's specific to SQLAlchemy's declarative system.
# However, SQLAlchemy's own stubs often type `declarative_base()` as returning `Any`.
# Given it's used as `class MyModel(Base):`, `type` (which is `Type[Any]`) or `Any` are common.
# Let's stick to `Any` for `Base` as it's less likely to cause issues with specific type checker versions
# and aligns with how SQLAlchemy stubs sometimes handle it, while acknowledging `DeclarativeMeta` or `Type[Model]`
# could be more semantically precise depending on interpretation.
# The task mentioned `Base: Type = ...` which implies `Type[Any]`.
Base: Any = declarative_base(
    cls=_Base,
    # metadata=metadata_obj # If metadata_obj were defined above
    metadata=None,  # metadata=None for Alembic, it will use its own with the convention
)


class TimestampMixin:
    """
    Миксин для добавления полей created_at и updated_at в модели.
    `created_at`: время создания записи.
    `updated_at`: время последнего обновления записи.
    """

    # Ensure `from datetime import datetime` is present
    # Using `datetime` (python type) for Mapped, SQLAlchemy handles conversion.
    # `nullable=False` is a good practice for these fields unless explicitly allowed.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # Storing with timezone is often recommended
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        comment="Время создания записи",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
        comment="Время последнего обновления записи",
    )


# Example PkModel as per task (not in original file, but for illustration)
# class PkModel:
#     id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)

# Example combined model base if PkModel and TimestampMixin were to be used together
# class Model(Base, PkModel, TimestampMixin):
#     __abstract__ = True
#     # Potential __table_args__ could be defined here if TableArgsMixin concept was used
#     # For example:
#     # @declared_attr
#     # def __table_args__(cls) -> Dict[str, Any]:
#     #     return {"mysql_engine": "InnoDB"}

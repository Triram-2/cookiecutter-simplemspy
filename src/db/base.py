import inflection
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.ext.declarative import declared_attr, DeclarativeMeta

convention: Dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class _Base:
    @declared_attr  # type: ignore[arg-type]
    def __tablename__(cls: Any) -> str:
        return inflection.tableize(cls.__name__)


Base: DeclarativeMeta = declarative_base(
    cls=_Base,
    metadata=None,
)


class TimestampMixin:
    """
    Mixin for adding created_at and updated_at timestamps to models.
    `created_at`: Time of record creation.
    `updated_at`: Time of last record update.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        comment="Time of record creation",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
        comment="Time of last record update",
    )

"""
Pydantic schemas for API data validation and database serialization/deserialization.

Guidelines:
1. Base schemas: Common fields (e.g., UserBase).
2. Create schemas: Inherit from base, add creation-specific fields (e.g., UserCreate).
3. Update schemas: Inherit from base, all fields Optional (e.g., UserUpdate).
4. Read/response schemas: Inherit from base (and common models like IDModel, TimestampModel),
   add fields for client response. Set `model_config = {"from_attributes": True}` for SQLAlchemy ORM compatibility.
"""

from .common import Msg, IDModel, TimestampModel, PaginationParams, PaginatedResponse

__all__ = ["IDModel", "Msg", "PaginatedResponse", "PaginationParams", "TimestampModel"]

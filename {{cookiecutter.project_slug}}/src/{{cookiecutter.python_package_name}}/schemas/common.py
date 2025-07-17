from datetime import datetime
from typing import List, TypeVar, ClassVar

from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class Msg(BaseModel):
    """Schema for simple API text messages."""

    message: str = Field(..., description="Text message from API")

    model_config: ClassVar[ConfigDict] = {
        "json_schema_extra": {"example": {"message": "Action completed successfully"}}
    }


class IDModel(BaseModel):
    """Base schema for models with an integer ID."""

    id: int = Field(
        ..., description="Unique identifier", json_schema_extra={"example": 1}
    )


class TimestampModel(BaseModel):
    """Base schema for models with timestamps."""

    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = {
        # Allows Pydantic to work correctly with ORM objects,
        # accessing attributes via model.attr instead of model['attr']
        "from_attributes": True
    }


class PaginationParams(BaseModel):
    """Parameters for API request pagination."""

    skip: int = Field(default=0, ge=0, description="Number of records to skip (offset)")
    limit: int = Field(
        default=100, ge=1, le=200, description="Maximum records per page (up to 200)"
    )


class PaginatedResponse[T](BaseModel):
    """Generic schema for paginated API responses."""

    items: List[T] = Field(..., description="List of items on the current page")
    total: int = Field(
        ..., description="Total number of items", json_schema_extra={"example": 100}
    )
    skip: int = Field(
        ..., description="Number of skipped items", json_schema_extra={"example": 0}
    )
    limit: int = Field(
        ..., description="Number of items per page", json_schema_extra={"example": 10}
    )

    model_config: ClassVar[ConfigDict] = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {"id": 1, "name": "Sample Object 1"},
                    {"id": 2, "name": "Sample Object 2"},
                ],
                "total": 2,
                "skip": 0,
                "limit": 10,
            }
        }
    }

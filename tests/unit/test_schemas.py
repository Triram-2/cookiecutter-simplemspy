import pytest
from datetime import datetime, timezone

from pydantic import BaseModel, ValidationError

from name.schemas.common import (
    Msg,
    IDModel,
    TimestampModel,
    PaginationParams,
    PaginatedResponse,
)
import name.schemas


def test_msg_schema():
    data = {"message": "Hello"}
    msg_instance = Msg(**data)
    assert msg_instance.message == "Hello"
    with pytest.raises(ValidationError):
        Msg(message=None)
    with pytest.raises(ValidationError):
        Msg()


def test_id_model_schema():
    data = {"id": 123}
    id_instance = IDModel(**data)
    assert id_instance.id == 123
    with pytest.raises(ValidationError):
        IDModel(id="abc")
    with pytest.raises(ValidationError):
        IDModel()


def test_timestamp_model_schema():
    now = datetime.now(timezone.utc)  # noqa: UP017
    data = {"created_at": now, "updated_at": now}
    ts_instance = TimestampModel(**data)
    assert ts_instance.created_at == now
    assert ts_instance.updated_at == now
    with pytest.raises(ValidationError):
        TimestampModel(created_at=now)


def test_pagination_params_schema():
    params_default = PaginationParams()
    assert params_default.skip == 0
    assert params_default.limit == 100

    data = {"skip": 10, "limit": 50}
    params_custom = PaginationParams(**data)
    assert params_custom.skip == 10
    assert params_custom.limit == 50

    with pytest.raises(ValidationError):
        PaginationParams(skip=-1)
    with pytest.raises(ValidationError):
        PaginationParams(limit=0)
    with pytest.raises(ValidationError):
        PaginationParams(limit=300)


class SampleItem(BaseModel):
    id: int
    name: str


def test_paginated_response_schema():
    item1 = SampleItem(id=1, name="Item 1")
    item2 = SampleItem(id=2, name="Item 2")
    data = {"items": [item1, item2], "total": 2, "skip": 0, "limit": 10}
    paginated_instance = PaginatedResponse[SampleItem](**data)
    assert len(paginated_instance.items) == 2
    assert paginated_instance.items[0].name == "Item 1"
    assert paginated_instance.total == 2

    with pytest.raises(ValidationError):
        PaginatedResponse[SampleItem](items=[item1], total=1, skip=0)  # Missing 'limit'


def test_schemas_init_exports():
    assert name.schemas.IDModel is IDModel
    assert name.schemas.Msg is Msg
    assert name.schemas.TimestampModel is TimestampModel
    assert name.schemas.PaginationParams is PaginationParams
    assert name.schemas.PaginatedResponse is PaginatedResponse

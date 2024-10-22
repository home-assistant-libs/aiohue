"""Test base controller functions."""

from dataclasses import dataclass
from unittest.mock import Mock
from uuid import uuid4

from aiohue import HueBridgeV2
from aiohue.v2 import EventType
from aiohue.v2.controllers.base import BaseResourcesController
from aiohue.v2.models.resource import ResourceTypes


@dataclass
class MockData:
    """Mock data resource type."""

    id: str
    type: ResourceTypes = ResourceTypes.UNKNOWN

    id_v1: str | None = None


class MockController(BaseResourcesController[type[MockData]]):
    """Controller for mock data resource."""

    item_type = ResourceTypes.UNKNOWN
    item_cls = MockData
    allow_parser_error = False


async def test_handle_event():
    """Test handling of events."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    controller = MockController(bridge)
    callback = Mock(return_value=None)
    controller.subscribe(callback)

    resource_id = str(uuid4())
    other_id = str(uuid4())

    evt_data = {
        "id": resource_id,
        "id_v1": "mock/1",
    }

    # Create a new resource
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_ADDED, evt_data)

    cur_data = MockData(
        id=resource_id,
        type=ResourceTypes.UNKNOWN,
        id_v1="mock/1",
    )
    callback.assert_called_once_with(EventType.RESOURCE_ADDED, cur_data)
    callback.reset_mock()

    evt_data = {
        "id": resource_id,
        "id_v1": "mock/2",
    }

    # Update of a single property of an existing resource
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_UPDATED, evt_data)

    cur_data = MockData(
        id=resource_id,
        type=ResourceTypes.UNKNOWN,
        id_v1="mock/2",
    )
    callback.assert_called_once_with(EventType.RESOURCE_UPDATED, cur_data)
    callback.reset_mock()

    evt_data = {
        "id": other_id,
        "id_v1": "mock/1",
    }

    # Update of a single property of a non-existing resource
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_UPDATED, evt_data)

    callback.assert_not_called()
    callback.reset_mock()

    evt_data = {
        "id": resource_id,
    }

    # Remove of existing resource
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_DELETED, evt_data)

    cur_data = MockData(
        id=resource_id,
        type=ResourceTypes.UNKNOWN,
        id_v1="mock/2",
    )
    callback.assert_called_once_with(EventType.RESOURCE_DELETED, cur_data)
    callback.reset_mock()

    evt_data = {
        "id": resource_id,
        "id_v1": "mock/2",
    }

    # Update of an already removed resource
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_UPDATED, evt_data)

    callback.assert_not_called()

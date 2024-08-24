"""Test base controller functions."""

from dataclasses import dataclass
from unittest.mock import Mock
from uuid import uuid4

from aiohue import HueBridgeV2
from aiohue.v2 import EventType
from aiohue.v2.controllers.base import BaseResourcesController
from aiohue.v2.controllers.sensors import ButtonController, RelativeRotaryController
from aiohue.v2.models.resource import ResourceIdentifier, ResourceTypes


@dataclass
class MockData:
    """Mock data resource type."""

    id: str
    type: ResourceTypes = ResourceTypes.UNKNOWN

    owner: ResourceIdentifier | None = None
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
    device_id = str(uuid4())

    evt_data = {
        "id": resource_id,
        "type": "unknown",
        "id_v1": "mock/1",
        "owner": {"rid": device_id, "rtype": "device"},
    }

    # Create a new resource
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_ADDED, evt_data, False)

    cur_data = MockData(
        id=resource_id,
        type=ResourceTypes.UNKNOWN,
        id_v1="mock/1",
        owner=ResourceIdentifier(rid=device_id, rtype=ResourceTypes.DEVICE),
    )
    callback.assert_called_with(EventType.RESOURCE_ADDED, cur_data)
    callback.reset_mock()

    evt_data = {
        "id": resource_id,
        "id_v1": "mock/2",
    }

    # Update of a single property of an existing resource
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_UPDATED, evt_data, False)

    cur_data = MockData(
        id=resource_id,
        type=ResourceTypes.UNKNOWN,
        id_v1="mock/2",
        owner=ResourceIdentifier(rid=device_id, rtype=ResourceTypes.DEVICE),
    )
    callback.assert_called_with(EventType.RESOURCE_UPDATED, cur_data)
    callback.reset_mock()

    evt_data = {
        "id": device_id,
        "id_v1": "mock/1",
    }

    # Update of a single property of a non-existing resource
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_UPDATED, evt_data, False)

    callback.assert_not_called()
    callback.reset_mock()

    evt_data = {
        "id": resource_id,
    }

    # Remove of existing resource
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_DELETED, evt_data, False)

    cur_data = MockData(
        id=resource_id,
        type=ResourceTypes.UNKNOWN,
        id_v1="mock/2",
        owner=ResourceIdentifier(rid=device_id, rtype=ResourceTypes.DEVICE),
    )
    callback.assert_called_with(EventType.RESOURCE_DELETED, cur_data)
    callback.reset_mock()

    evt_data = {
        "id": resource_id,
        "id_v1": "mock/2",
    }

    # Update of an already removed resource
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_UPDATED, evt_data, False)

    callback.assert_not_called()


def test_handle_last_event_backwards_compatibility_for_button():
    """Test backwards compatibility handling for last_event in button."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    button_controller = ButtonController(bridge)

    evt_data = {"button": {"last_event": "initial_press"}}

    # pylint: disable=protected-access
    button_controller._handle_last_event_backwards_compatibility(evt_data)

    assert (
        evt_data.get("button", {}).get("button_report", {}).get("event")
        == "initial_press"
    )

    evt_data = {
        "button": {
            "last_event": "initial_press",
            "button_report": {"event": "short_release"},
        }
    }

    # pylint: disable=protected-access
    button_controller._handle_last_event_backwards_compatibility(evt_data)

    assert (
        evt_data.get("button", {}).get("button_report", {}).get("event")
        == "short_release"
    )

    evt_data = {"button": {}}

    # pylint: disable=protected-access
    button_controller._handle_last_event_backwards_compatibility(evt_data)

    assert evt_data.get("button", {}).get("button_report") is None


def test_handle_last_event_backwards_compatibility_for_relative_rotary():
    """Test backwards compatibility handling for last_event in relative_rotary."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    rotary_controller = RelativeRotaryController(bridge)

    evt_data = {
        "relative_rotary": {
            "last_event": {
                "action": "start",
                "rotation": {"direction": "clock_wise", "steps": 1, "duration": 800},
            }
        }
    }

    # pylint: disable=protected-access
    rotary_controller._handle_last_event_backwards_compatibility(evt_data)

    assert (
        evt_data.get("relative_rotary", {}).get("rotary_report", {}).get("action")
        == "start"
    )
    assert evt_data.get("relative_rotary", {}).get("rotary_report", {}).get(
        "rotation"
    ) == evt_data.get("relative_rotary", {}).get("last_event", {}).get("rotation")

    evt_data = {
        "relative_rotary": {
            "last_event": {
                "action": "start",
                "rotation": {"direction": "clock_wise", "steps": 1, "duration": 800},
            },
            "rotary_report": {
                "action": "repeat",
                "rotation": {
                    "direction": "counter_clock_wise",
                    "steps": 1,
                    "duration": 800,
                },
            },
        }
    }

    # pylint: disable=protected-access
    rotary_controller._handle_last_event_backwards_compatibility(evt_data)

    assert (
        evt_data.get("relative_rotary", {}).get("rotary_report", {}).get("action")
        == "repeat"
    )
    assert (
        evt_data.get("relative_rotary", {})
        .get("rotary_report", {})
        .get("rotation", {})
        .get("direction")
        == "counter_clock_wise"
    )
    assert (
        evt_data.get("relative_rotary", {})
        .get("rotary_report", {})
        .get("rotation", {})
        .get("steps")
        == 1
    )
    assert (
        evt_data.get("relative_rotary", {})
        .get("rotary_report", {})
        .get("rotation", {})
        .get("duration")
        == 800
    )

    evt_data = {"relative_rotary": {}}

    # pylint: disable=protected-access
    rotary_controller._handle_last_event_backwards_compatibility(evt_data)

    assert evt_data.get("relative_rotary", {}).get("rotary_report") is None

"""Test base controller functions."""

from dataclasses import dataclass
from unittest.mock import Mock
from uuid import uuid4

from aiohue import HueBridgeV2
from aiohue.v2 import EventType
from aiohue.v2.controllers.base import BaseResourcesController
from aiohue.v2.controllers.sensors import ButtonController, RelativeRotaryController
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


def test_handle_last_event_backwards_compatibility_for_button():
    """Test backwards compatibility handling for last_event in button."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    button_controller = ButtonController(bridge)

    evt_data = {"button": {"last_event": "initial_press"}}

    # pylint: disable=protected-access
    button_controller._handle_last_event_backwards_compatibility(evt_data)

    button_report = evt_data.get("button", {}).get("button_report", {})
    assert button_report.get("event") == "initial_press"
    assert button_report.get("updated")

    evt_data = {
        "button": {
            "last_event": "initial_press",
            "button_report": {
                "event": "short_release",
                "updated": "2024-08-24T16:27:00Z",
            },
        }
    }

    # pylint: disable=protected-access
    button_controller._handle_last_event_backwards_compatibility(evt_data)

    button_report = evt_data.get("button", {}).get("button_report", {})
    assert button_report.get("event") == "short_release"
    assert button_report.get("updated") == "2024-08-24T16:27:00Z"

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

    rotary_report = evt_data.get("relative_rotary", {}).get("rotary_report", {})
    assert rotary_report.get("action") == "start"
    assert rotary_report.get("rotation") == evt_data.get("relative_rotary", {}).get(
        "last_event", {}
    ).get("rotation")
    assert rotary_report.get("updated")

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
                "updated": "2024-08-24T16:27:00Z",
            },
        }
    }

    # pylint: disable=protected-access
    rotary_controller._handle_last_event_backwards_compatibility(evt_data)

    rotary_report = evt_data.get("relative_rotary", {}).get("rotary_report", {})
    assert rotary_report.get("action") == "repeat"
    assert rotary_report.get("rotation", {}).get("direction") == "counter_clock_wise"
    assert rotary_report.get("rotation", {}).get("steps") == 1
    assert rotary_report.get("rotation", {}).get("duration") == 800
    assert rotary_report.get("updated") == "2024-08-24T16:27:00Z"

    evt_data = {"relative_rotary": {}}

    # pylint: disable=protected-access
    rotary_controller._handle_last_event_backwards_compatibility(evt_data)

    assert evt_data.get("relative_rotary", {}).get("rotary_report") is None

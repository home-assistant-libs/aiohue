"""Test button controller functions."""

import asyncio
from copy import deepcopy
from unittest.mock import Mock
from uuid import uuid4

from aiohue import HueBridgeV2
from aiohue.v2 import EventType
from aiohue.v2.controllers.sensors import ButtonController
from aiohue.v2.models.button import ButtonEvent
from aiohue.v2.models.resource import ResourceTypes


async def create_button(
    controller: ButtonController, callback: Mock, button_id: str, device_id: str
):
    """Create a button resource."""
    evt_data = {
        "id": button_id,
        "metadata": {"control_id": 1},
        "button": {
            "event_values": [
                "initial_press",
                "repeat",
                "short_release",
                "long_release",
                "long_press",
            ],
            "repeat_interval": 800,
        },
        "owner": {"rid": device_id, "rtype": ResourceTypes.DEVICE},
    }

    # Create a new resource
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_ADDED, evt_data)

    callback.assert_called_once()
    callback.reset_mock()


async def create_device(
    bridge: HueBridgeV2, device_id: str, model_id: str, button_id: str
):
    """Create a device resource."""
    evt_data = {
        "id": device_id,
        "services": [{"rid": button_id, "rtype": "button"}],
        "product_data": {
            "model_id": model_id,
            "manufacturer_name": "Signify",
            "product_name": "Hue Light",
            "product_archetype": "classic_bulb",
            "certified": True,
            "software_version": "1.0.0",
        },
        "metadata": {"archetype": "classic_bulb", "name": "Kitchen"},
    }

    # pylint: disable=protected-access
    await bridge.devices._handle_event(EventType.RESOURCE_ADDED, evt_data)


def generate_button_event_data(button_id: str, event: str, device_id: str):
    """Generate button event data."""
    return {
        "id": button_id,
        "button": {
            "button_report": {
                "event": event,
                "updated": "2024-08-24T16:24:00.0Z",
            }
        },
        "owner": {"rid": device_id, "rtype": ResourceTypes.DEVICE},
    }


async def handle_button_event(
    controller: ButtonController, button_id: str, event: str, device_id: str
):
    """Handle button event."""
    # pylint: disable=protected-access
    await controller._handle_event(
        EventType.RESOURCE_UPDATED,
        generate_button_event_data(button_id, event, device_id),
    )


class CopyingMock(Mock):
    """Mock that deep copies its arguments."""

    def __call__(self, *args, **kwargs):
        args = deepcopy(args)
        kwargs = deepcopy(kwargs)
        return super().__call__(*args, **kwargs)


async def test_handle_events():
    """Test handling of events."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    controller = ButtonController(bridge)
    callback = CopyingMock(return_value=None)
    controller.subscribe(callback)

    button_id = str(uuid4())
    device_id = str(uuid4())

    await create_button(controller, callback, button_id, device_id)

    # Button event
    await handle_button_event(controller, button_id, "initial_press", device_id)

    callback.assert_called_once()
    assert (
        callback.call_args.args[1].button.button_report.event
        == ButtonEvent.INITIAL_PRESS
    )
    callback.reset_mock()

    evt_data = {
        "id": button_id,
        "owner": {"rid": device_id, "rtype": ResourceTypes.DEVICE},
    }

    # Absent button report is dropped
    # pylint: disable=protected-access
    await controller._handle_event(EventType.RESOURCE_UPDATED, evt_data)

    callback.assert_not_called()
    callback.reset_mock()


async def test_handle_events_button_workaround_short_release():
    """Test handling of events for device requiring button workaround."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    controller = ButtonController(bridge)
    callback = CopyingMock(return_value=None)
    controller.subscribe(callback)

    button_id = str(uuid4())
    device_id = str(uuid4())

    await create_device(bridge, device_id, "FOHSWITCH", button_id)
    await create_button(controller, callback, button_id, device_id)

    # Button event: initial_press
    await handle_button_event(controller, button_id, "initial_press", device_id)

    await asyncio.sleep(1.2)

    # Button event: short_release
    await handle_button_event(controller, button_id, "short_release", device_id)

    callback.assert_called()
    assert callback.call_count == 2
    assert (
        callback.call_args_list[0].args[1].button.button_report.event
        == ButtonEvent.INITIAL_PRESS
    )
    assert (
        callback.call_args_list[1].args[1].button.button_report.event
        == ButtonEvent.SHORT_RELEASE
    )


async def test_handle_events_button_workaround_repeats():
    """Test handling of events for device requiring button workaround."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    controller = ButtonController(bridge)
    callback = CopyingMock(return_value=None)
    controller.subscribe(callback)

    button_id = str(uuid4())
    device_id = str(uuid4())

    await create_device(bridge, device_id, "FOHSWITCH", button_id)
    await create_button(controller, callback, button_id, device_id)

    # Button event: initial_press
    await handle_button_event(controller, button_id, "initial_press", device_id)

    await asyncio.sleep(2.2)

    # Button event: short_release
    await handle_button_event(controller, button_id, "short_release", device_id)

    callback.assert_called()
    assert callback.call_count == 4
    assert (
        callback.call_args_list[0].args[1].button.button_report.event
        == ButtonEvent.INITIAL_PRESS
    )
    assert (
        callback.call_args_list[1].args[1].button.button_report.event
        == ButtonEvent.REPEAT
    )
    assert (
        callback.call_args_list[2].args[1].button.button_report.event
        == ButtonEvent.REPEAT
    )
    assert (
        callback.call_args_list[3].args[1].button.button_report.event
        == ButtonEvent.SHORT_RELEASE
    )


async def test_handle_events_button_workaround_long_release():
    """Test handling of events for device requiring button workaround."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    controller = ButtonController(bridge)
    callback = CopyingMock(return_value=None)
    controller.subscribe(callback)

    button_id = str(uuid4())
    device_id = str(uuid4())

    await create_device(bridge, device_id, "FOHSWITCH", button_id)
    await create_button(controller, callback, button_id, device_id)

    # Button event: initial_press
    await handle_button_event(controller, button_id, "initial_press", device_id)

    await asyncio.sleep(12.7)

    callback.assert_called()
    assert callback.call_count == 23
    assert (
        callback.call_args_list[22].args[1].button.button_report.event
        == ButtonEvent.LONG_RELEASE
    )


async def test_handle_events_button_workaround_interrupt():
    """Test handling of events for device requiring button workaround."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    controller = ButtonController(bridge)
    callback = CopyingMock(return_value=None)
    controller.subscribe(callback)

    button1_id = str(uuid4())
    button2_id = str(uuid4())
    device1_id = str(uuid4())
    device2_id = str(uuid4())

    await create_device(bridge, device1_id, "FOHSWITCH", button1_id)
    await create_device(bridge, device2_id, "ZGPSWITCH", button2_id)
    await create_button(controller, callback, button1_id, device1_id)
    await create_button(controller, callback, button2_id, device2_id)

    # Button event: initial_press
    await handle_button_event(controller, button1_id, "initial_press", device1_id)

    await asyncio.sleep(2.2)

    # Button event: initial_press
    await handle_button_event(controller, button2_id, "initial_press", device2_id)

    callback.assert_called()
    assert callback.call_count == 4
    assert (
        callback.call_args_list[0].args[1].button.button_report.event
        == ButtonEvent.INITIAL_PRESS
    )
    assert (
        callback.call_args_list[1].args[1].button.button_report.event
        == ButtonEvent.REPEAT
    )
    assert (
        callback.call_args_list[2].args[1].button.button_report.event
        == ButtonEvent.REPEAT
    )
    assert callback.call_args_list[3].args[1].id == button2_id
    assert (
        callback.call_args_list[3].args[1].button.button_report.event
        == ButtonEvent.INITIAL_PRESS
    )


async def test_handle_events_button_non_workaround_device():
    """Test handling of events for device requiring button workaround."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    controller = ButtonController(bridge)
    callback = CopyingMock(return_value=None)
    controller.subscribe(callback)

    button_id = str(uuid4())
    device_id = str(uuid4())

    await create_device(bridge, device_id, "ZGPSWITCH", button_id)
    await create_button(controller, callback, button_id, device_id)

    # Button event: initial_press
    await handle_button_event(controller, button_id, "initial_press", device_id)

    await asyncio.sleep(2.2)

    # Button event: short_release
    await handle_button_event(controller, button_id, "short_release", device_id)

    callback.assert_called()
    assert callback.call_count == 2
    assert (
        callback.call_args_list[0].args[1].button.button_report.event
        == ButtonEvent.INITIAL_PRESS
    )
    assert (
        callback.call_args_list[1].args[1].button.button_report.event
        == ButtonEvent.SHORT_RELEASE
    )

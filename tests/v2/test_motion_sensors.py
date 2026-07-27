"""Test motion sensor parsing and reported state."""

from uuid import uuid4

from aiohue import HueBridgeV2
from aiohue.v2 import EventType
from aiohue.v2.controllers.sensors import SecurityAreaMotionController


def security_area_motion_data(sensor_id: str, motion: dict | None) -> dict:
    """Build a security_area_motion resource, optionally without a motion feature."""
    data = {
        "id": sensor_id,
        "owner": {"rid": str(uuid4()), "rtype": "motion_area_configuration"},
        "enabled": True,
        "sensitivity": {"sensitivity": 2, "sensitivity_max": 4},
        "type": "security_area_motion",
    }
    if motion is not None:
        data["motion"] = motion
    return data


async def test_motion_omitted_by_bridge_still_parses():
    """A sensor that reports no motion feature at all must not be dropped."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    controller = SecurityAreaMotionController(bridge)
    sensor_id = str(uuid4())

    # pylint: disable=protected-access
    await controller._handle_event(
        EventType.RESOURCE_ADDED, security_area_motion_data(sensor_id, None)
    )

    assert sensor_id in controller
    assert controller[sensor_id].motion is None


async def test_motion_value_is_none_when_not_valid():
    """An invalid reading is unknown, not an observation of "no motion"."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    controller = SecurityAreaMotionController(bridge)
    sensor_id = str(uuid4())

    # motion_report can hold an arbitrarily old value while motion_valid is false
    # pylint: disable=protected-access
    await controller._handle_event(
        EventType.RESOURCE_ADDED,
        security_area_motion_data(
            sensor_id,
            {
                "motion": False,
                "motion_valid": False,
                "motion_report": {
                    "changed": "2025-09-23T11:34:14.403Z",
                    "motion": False,
                },
            },
        ),
    )

    assert controller[sensor_id].motion.value is None


async def test_motion_value_prefers_report_when_valid():
    """A valid reading is taken from the motion report."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    controller = SecurityAreaMotionController(bridge)
    sensor_id = str(uuid4())

    # pylint: disable=protected-access
    await controller._handle_event(
        EventType.RESOURCE_ADDED,
        security_area_motion_data(
            sensor_id,
            {
                "motion": False,
                "motion_valid": True,
                "motion_report": {
                    "changed": "2026-07-27T06:44:23.013Z",
                    "motion": True,
                },
            },
        ),
    )

    assert controller[sensor_id].motion.value is True

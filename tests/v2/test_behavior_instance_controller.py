"""Test behavior instance controller."""

from unittest.mock import patch

import pytest

from aiohue import HueBridgeV2
from aiohue.v2.models.behavior_instance import (
    BehaviorInstance,
    PresenceMimickingState,
)

BEHAVIOR_INSTANCE_ID = "ac390cd0-d0b6-208d-5e60-b1653803c88d"
ENDPOINT = f"clip/v2/resource/behavior_instance/{BEHAVIOR_INSTANCE_ID}"


@pytest.fixture(name="bridge")
async def bridge_fixture(v2_resources) -> HueBridgeV2:
    """Return a bridge with the v2 resources loaded."""
    bridge = HueBridgeV2("192.168.1.123", "mock-key")
    with patch.object(bridge, "request", return_value=v2_resources):
        await bridge.fetch_full_state()
    return bridge


@pytest.mark.parametrize(
    ("action", "expected"),
    [("start", {"start": {}}), ("stop", {"stop": {}})],
)
async def test_start_stop(bridge: HueBridgeV2, action: str, expected: dict) -> None:
    """Test start and stop send a trigger instead of touching enabled."""
    controller = bridge.config.behavior_instance

    with patch.object(bridge, "request", return_value=None) as mock_request:
        await getattr(controller, action)(BEHAVIOR_INSTANCE_ID)

    mock_request.assert_called_once_with("put", ENDPOINT, json={"trigger": expected})


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ({"pm_state": "started"}, PresenceMimickingState.STARTED),
        ({"pm_state": "stopped"}, PresenceMimickingState.STOPPED),
        ({"pm_state": "something_new"}, PresenceMimickingState.UNKNOWN),
        ({"source_type": "device"}, None),
        ({}, None),
        (None, None),
    ],
)
async def test_presence_mimicking_state(
    bridge: HueBridgeV2, state: dict | None, expected: PresenceMimickingState | None
) -> None:
    """Test the run state is only reported for presence mimicking instances."""
    item: BehaviorInstance = bridge.config.behavior_instance[BEHAVIOR_INSTANCE_ID]
    item.state = state

    assert item.presence_mimicking_state is expected

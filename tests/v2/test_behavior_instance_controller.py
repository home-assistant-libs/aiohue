"""Test behavior instance controller."""

from unittest.mock import patch

import pytest

from aiohue import HueBridgeV2

BEHAVIOR_INSTANCE_ID = "ac390cd0-d0b6-208d-5e60-b1653803c88d"


@pytest.fixture(name="bridge")
async def bridge_fixture(v2_resources) -> HueBridgeV2:
    """Return a bridge with the v2 resources loaded."""
    bridge = HueBridgeV2("192.168.1.123", "mock-key")
    with patch.object(bridge, "request", return_value=v2_resources):
        await bridge.fetch_full_state()
    return bridge


@pytest.mark.parametrize("enabled", [True, False])
async def test_set_enabled_resends_configuration(
    bridge: HueBridgeV2, enabled: bool
) -> None:
    """Test set_enabled sends the current configuration along with enabled.

    The bridge rejects a PUT that only carries `enabled` with
    "The instance doesn't support triggers.".
    """
    controller = bridge.config.behavior_instance
    configuration = controller[BEHAVIOR_INSTANCE_ID].configuration

    with patch.object(bridge, "request", return_value=None) as mock_request:
        await controller.set_enabled(BEHAVIOR_INSTANCE_ID, enabled)

    mock_request.assert_called_once_with(
        "put",
        f"clip/v2/resource/behavior_instance/{BEHAVIOR_INSTANCE_ID}",
        json={"enabled": enabled, "configuration": configuration},
    )


async def test_set_enabled_unknown_id(bridge: HueBridgeV2) -> None:
    """Test set_enabled on an id that is not cached omits the configuration."""
    with patch.object(bridge, "request", return_value=None) as mock_request:
        await bridge.config.behavior_instance.set_enabled("not-a-known-id", True)

    mock_request.assert_called_once_with(
        "put",
        "clip/v2/resource/behavior_instance/not-a-known-id",
        json={"enabled": True},
    )

"""Test v2 bridge."""

from unittest.mock import patch

from aiohue import HueBridgeV2


async def test_bridge_init(v2_resources):
    """Test v2 bridge."""
    bridge = HueBridgeV2("192.168.1.123", "mock-key")
    assert bridge.host == "192.168.1.123"

    with patch.object(bridge, "request", return_value=v2_resources):
        await bridge.fetch_full_state()

    assert bridge.config is not None
    assert bridge.config.bridge_id == "aabbccddeeffggh"

    assert bridge.devices is not None
    assert len(bridge.devices.get_lights("42b8327b-b7d7-2469-3c45-069a41b4dca8")) == 1
    assert len(bridge.devices.get_sensors("fb657eb4-38ba-fd3c-7535-d56f4350699f")) == 5

    assert bridge.lights is not None
    assert bridge.scenes is not None
    assert bridge.speakers is not None
    assert len(bridge.devices.get_speakers("b6257363-71db-1b79-10d8-69c4e3dcdae4")) == 1
    assert bridge.sensors is not None
    assert bridge.groups is not None

    # test required version check (fixture bridge runs 1.78.2071401010)
    assert bridge.config.check_version("1.79.2071401010") is False
    assert bridge.config.check_version("1.78.2071401010") is True
    assert bridge.config.check_version("1.50.1950111030") is True

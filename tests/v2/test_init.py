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
    assert len(bridge.devices.get_lights("0b216218-d811-4c95-8c55-bbcda50f9d50")) == 1
    assert len(bridge.devices.get_sensors("342daec9-391b-480b-abdd-87f1aa04ce3b")) == 6

    assert bridge.lights is not None
    assert bridge.scenes is not None
    assert bridge.sensors is not None
    assert bridge.groups is not None

    # test required version check
    assert bridge.config.check_version("1.50.1950111030") == False
    assert bridge.config.check_version("1.48.1948086000") == True
    assert bridge.config.check_version("1.48.1948085000") == True

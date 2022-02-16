"""Test v1 bridge."""

from aiohue import HueBridgeV1


async def test_bridge_init():
    """Test v1 bridge."""
    bridge = HueBridgeV1("192.168.1.123", "mock-key")
    assert bridge.host == "192.168.1.123"

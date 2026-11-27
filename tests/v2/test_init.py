"""Test v2 bridge."""

from unittest.mock import MagicMock, patch

import aiohttp

from aiohue import HueBridgeV2
from aiohue.v2.controllers.events import KEEPALIVE_INTERVAL


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


async def test_idle_connections_outlive_the_keepalive_interval():
    """Test idle connections stay pooled longer than the event stream keepalive.

    The keepalive request then keeps a connection to the bridge open, so a
    request after a pause doesn't need a new TCP connection and TLS handshake.
    """
    bridge = HueBridgeV2("192.168.1.123", "mock-key")
    response = MagicMock()
    with (
        patch("aiohttp.TCPConnector", wraps=aiohttp.TCPConnector) as connector,
        patch("aiohttp.ClientSession.request", return_value=response),
    ):
        async with bridge.create_request("get", "clip/v2/resource"):
            pass
        await bridge.close()

    assert connector.call_args.kwargs["keepalive_timeout"] > KEEPALIVE_INTERVAL

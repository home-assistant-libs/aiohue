"""Test the discovery module."""

from contextlib import asynccontextmanager
from unittest.mock import Mock

import aiohttp
import pytest

from aiohue.discovery import is_hue_bridge

BRIDGE_CONFIG = {"name": "Hue Bridge", "bridgeid": "ECB5FAFFFE312CED"}


def mock_session(responses: dict[str, dict | Exception]) -> Mock:
    """Return a mock ClientSession that answers per URL scheme."""
    session = Mock(spec=aiohttp.ClientSession)

    @asynccontextmanager
    async def _get(url: str, **_kwargs):
        answer = responses[url.split(":", 1)[0]]
        if isinstance(answer, Exception):
            raise answer
        resp = Mock(spec=aiohttp.ClientResponse)

        async def _json():
            return answer

        resp.json = _json
        yield resp

    session.get = Mock(side_effect=_get)
    return session


async def test_is_hue_bridge_https() -> None:
    """Test the bridge id is returned from the https call without an http call."""
    session = mock_session({"https": BRIDGE_CONFIG})

    assert await is_hue_bridge("1.2.3.4", session) == "ecb5fa312ced"
    assert session.get.call_count == 1


async def test_is_hue_bridge_http_blocked() -> None:
    """Test a bridge that blocks plain http is found over https."""
    session = mock_session(
        {
            "https": BRIDGE_CONFIG,
            "http": aiohttp.ClientResponseError(Mock(), (), status=403),
        }
    )

    assert await is_hue_bridge("1.2.3.4", session) == "ecb5fa312ced"
    assert session.get.call_count == 1


async def test_is_hue_bridge_http_fallback() -> None:
    """Test http is used when the https call cannot connect."""
    session = mock_session(
        {
            "https": aiohttp.ClientConnectionError(),
            "http": BRIDGE_CONFIG,
        }
    )

    assert await is_hue_bridge("1.2.3.4", session) == "ecb5fa312ced"
    assert session.get.call_count == 2


async def test_is_hue_bridge_not_reachable() -> None:
    """Test the http error is raised when neither https nor http works."""
    session = mock_session(
        {
            "https": aiohttp.ClientConnectionError(),
            "http": aiohttp.ClientConnectionError("http failed"),
        }
    )

    with pytest.raises(aiohttp.ClientConnectionError, match="http failed"):
        await is_hue_bridge("1.2.3.4", session)


async def test_is_hue_bridge_emulator() -> None:
    """Test a response without a bridge id is rejected."""
    session = mock_session({"https": {"name": "Fake"}, "http": {"name": "Fake"}})

    with pytest.raises(aiohttp.ClientConnectionError, match="not a real Hue bridge"):
        await is_hue_bridge("1.2.3.4", session)

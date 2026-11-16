"""Test the util module."""

from contextlib import asynccontextmanager
from unittest.mock import Mock

import aiohttp
import pytest

from aiohue.errors import LinkButtonNotPressed
from aiohue.util import create_app_key


def mock_session(responses: dict[str, list | Exception]) -> Mock:
    """Return a mock ClientSession that answers per URL scheme."""
    session = Mock(spec=aiohttp.ClientSession)

    @asynccontextmanager
    async def _post(url: str, **_kwargs):
        answer = responses[url.split(":", 1)[0]]
        if isinstance(answer, Exception):
            raise answer
        resp = Mock(spec=aiohttp.ClientResponse)

        async def _json():
            return answer

        resp.json = _json
        yield resp

    session.post = Mock(side_effect=_post)
    return session


async def test_create_app_key_https() -> None:
    """Test the app key is returned from the https call."""
    session = mock_session({"https": [{"success": {"username": "app-key"}}]})

    assert await create_app_key("1.2.3.4", "test", session) == "app-key"


async def test_create_app_key_link_button_not_pressed() -> None:
    """Test a bridge error over https is raised without an http retry."""
    session = mock_session(
        {
            "https": [
                {
                    "error": {
                        "type": 101,
                        "address": "",
                        "description": "link button not pressed",
                    }
                }
            ],
            "http": [
                {
                    "error": {
                        "type": 4,
                        "address": "/",
                        "description": "method, GET, not available for resource, /",
                    }
                }
            ],
        }
    )

    with pytest.raises(LinkButtonNotPressed):
        await create_app_key("1.2.3.4", "test", session)
    assert session.post.call_count == 1


async def test_create_app_key_http_fallback() -> None:
    """Test http is used when the https call cannot connect."""
    session = mock_session(
        {
            "https": aiohttp.ClientConnectionError(),
            "http": [{"success": {"username": "app-key"}}],
        }
    )

    assert await create_app_key("1.2.3.4", "test", session) == "app-key"

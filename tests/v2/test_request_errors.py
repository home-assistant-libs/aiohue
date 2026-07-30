"""Test error handling of the v2 request method."""

from contextlib import asynccontextmanager
from unittest.mock import Mock, patch

import aiohttp
import pytest

from aiohue import HueBridgeV2
from aiohue.errors import AiohueException, Unauthorized


def mock_response(status: int, payload: dict | None, *, json_error: bool = False):
    """Return a mock ClientResponse."""
    resp = Mock(spec=aiohttp.ClientResponse)
    resp.status = status

    async def _json():
        if json_error:
            raise aiohttp.ContentTypeError(Mock(), ())
        return payload

    resp.json = _json

    def _raise_for_status():
        if status >= 400:
            raise aiohttp.ClientResponseError(
                Mock(), (), status=status, message="Bad Request"
            )

    resp.raise_for_status = _raise_for_status
    return resp


def patch_response(bridge: HueBridgeV2, resp):
    """Patch create_request to yield the given response."""

    @asynccontextmanager
    async def _create_request(_method: str, _path: str, **_kwargs):
        yield resp

    return patch.object(bridge, "create_request", _create_request)


async def test_error_description_is_raised() -> None:
    """Test the CLIP error description survives a 4xx status.

    Without this the caller only sees "400, message='Bad Request'" because
    raise_for_status() fires before the body is parsed.
    """
    bridge = HueBridgeV2("192.168.1.123", "mock-key")
    resp = mock_response(
        400,
        {
            "data": [],
            "errors": [{"description": "The instance doesn't support triggers."}],
        },
    )

    with patch_response(bridge, resp), pytest.raises(AiohueException) as err:
        await bridge.request("put", "clip/v2/resource/behavior_instance/1234")

    assert str(err.value) == "The instance doesn't support triggers."


async def test_error_status_without_body() -> None:
    """Test a 4xx without a parsable body still raises for status."""
    bridge = HueBridgeV2("192.168.1.123", "mock-key")
    resp = mock_response(400, None, json_error=True)

    with patch_response(bridge, resp), pytest.raises(aiohttp.ClientResponseError):
        await bridge.request("get", "clip/v2/resource/light")


async def test_forbidden_raises_unauthorized() -> None:
    """Test a 403 raises Unauthorized."""
    bridge = HueBridgeV2("192.168.1.123", "mock-key")

    with (
        patch_response(bridge, mock_response(403, None)),
        pytest.raises(Unauthorized),
    ):
        await bridge.request("get", "clip/v2/resource/light")


async def test_successful_request_returns_data() -> None:
    """Test a successful request returns the data key."""
    bridge = HueBridgeV2("192.168.1.123", "mock-key")
    resp = mock_response(200, {"data": [{"id": "1234"}], "errors": []})

    with patch_response(bridge, resp):
        result = await bridge.request("get", "clip/v2/resource/light")

    assert result == [{"id": "1234"}]

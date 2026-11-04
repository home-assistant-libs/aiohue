"""Test lights controller functions."""

from unittest.mock import AsyncMock, patch

import pytest

from aiohue import HueBridgeV2
from aiohue.v2.models.feature import GradientMode

LIGHT_ID = "01b1da1b-2cb1-eb71-5391-63b5ae1ceb6c"
POINTS = [(0.1, 0.2), (0.3, 0.4)]
POINTS_BODY = [
    {"color": {"xy": {"x": 0.1, "y": 0.2}}},
    {"color": {"xy": {"x": 0.3, "y": 0.4}}},
]


@pytest.mark.parametrize(
    ("kwargs", "expected_gradient"),
    [
        pytest.param(
            {
                "gradient_points": POINTS,
                "gradient_mode": GradientMode.SEGMENTED_PALETTE,
            },
            {"points": POINTS_BODY, "mode": "segmented_palette"},
            id="points_and_mode",
        ),
        pytest.param(
            {"gradient_points": POINTS},
            {"points": POINTS_BODY},
            id="points_without_mode",
        ),
        pytest.param({"on": True}, None, id="no_gradient"),
    ],
)
async def test_set_state_gradient(
    v2_resources, kwargs: dict, expected_gradient: dict | None
) -> None:
    """Gradient points and mode are sent only when requested."""
    bridge = HueBridgeV2("127.0.0.1", "fake")

    with patch.object(bridge, "request", return_value=v2_resources):
        await bridge.fetch_full_state()

    with patch.object(bridge, "request", new=AsyncMock()) as request:
        await bridge.lights.set_state(LIGHT_ID, **kwargs)

    body = request.call_args.kwargs["json"]
    assert body.get("gradient") == expected_gradient
    assert ("gradient" in body) == (expected_gradient is not None)

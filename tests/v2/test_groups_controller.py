"""Test group controller functions."""

from copy import deepcopy
from unittest.mock import patch

import pytest

from aiohue import HueBridgeV2

ROOM_ID = "6fbbf09d-87b1-a7a1-e347-0c574f92ae3f"
ZONE_ID = "2a6c3bd5-12e4-7d7f-f8b4-1b75c193e373"
LIGHT_1 = "24d60506-22e8-f564-cff5-c7b702b62504"
LIGHT_2 = "4cd1e047-6b7d-c797-eac8-3cb2b496ae36"
LIGHT_3 = "7ebc892a-46fe-0a90-cd0c-87836247edda"
LIGHT_4 = "f427202e-d8cd-cb0e-479f-72955a2d7cbe"


@pytest.mark.parametrize(
    ("reversed_groups", "room_lights", "zone_lights"),
    [
        pytest.param(
            set(),
            [LIGHT_1, LIGHT_2, LIGHT_3, LIGHT_4],
            [LIGHT_3, LIGHT_4],
            id="fixture_order",
        ),
        pytest.param(
            {ROOM_ID, ZONE_ID},
            [LIGHT_4, LIGHT_3, LIGHT_2, LIGHT_1],
            [LIGHT_4, LIGHT_3],
            id="reversed_children",
        ),
    ],
)
async def test_get_lights_follows_children_order(
    v2_resources: list[dict],
    reversed_groups: set[str],
    room_lights: list[str],
    zone_lights: list[str],
) -> None:
    """Room and zone lights are returned in the order of the group's children."""
    resources = deepcopy(v2_resources)
    for resource in resources:
        if resource["id"] in reversed_groups:
            resource["children"].reverse()
    bridge = HueBridgeV2("127.0.0.1", "fake")
    with patch.object(bridge, "request", return_value=resources):
        await bridge.fetch_full_state()

    assert [light.id for light in bridge.groups.room.get_lights(ROOM_ID)] == room_lights
    assert [light.id for light in bridge.groups.zone.get_lights(ZONE_ID)] == zone_lights


async def test_get_lights_ignores_duplicate_references(
    v2_resources: list[dict],
) -> None:
    """Duplicate children or light services return each light only once."""
    resources = deepcopy(v2_resources)
    resources_by_id = {resource["id"]: resource for resource in resources}
    room = resources_by_id[ROOM_ID]
    room["children"].append(room["children"][0])
    device = resources_by_id[room["children"][0]["rid"]]
    device["services"] = device["services"] + device["services"]
    zone = resources_by_id[ZONE_ID]
    zone["children"].append(zone["children"][0])
    bridge = HueBridgeV2("127.0.0.1", "fake")
    with patch.object(bridge, "request", return_value=resources):
        await bridge.fetch_full_state()

    assert [light.id for light in bridge.groups.room.get_lights(ROOM_ID)] == [
        LIGHT_1,
        LIGHT_2,
        LIGHT_3,
        LIGHT_4,
    ]
    assert [light.id for light in bridge.groups.zone.get_lights(ZONE_ID)] == [
        LIGHT_3,
        LIGHT_4,
    ]

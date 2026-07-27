"""Test scenes controller functions."""

from unittest.mock import patch

from aiohue import HueBridgeV2


async def test_get_group_returns_none_for_unresolvable_group(v2_resources):
    """A scene attached to a resource outside bridge.groups resolves to None."""
    bridge = HueBridgeV2("127.0.0.1", "fake")

    with patch.object(bridge, "request", return_value=v2_resources):
        await bridge.fetch_full_state()

    scene = next(iter(bridge.scenes.scene))
    # bridge_home is a legal scene group on the bridge but is not part of
    # bridge.groups, so it stands in for any group we cannot resolve
    scene.group.rid = "does-not-exist"

    assert bridge.scenes.scene.get_group(scene.id) is None
    assert bridge.scenes.get_group(scene.id) is None


async def test_get_group_resolves_known_group(v2_resources):
    """A scene attached to a room or zone resolves to that group."""
    bridge = HueBridgeV2("127.0.0.1", "fake")

    with patch.object(bridge, "request", return_value=v2_resources):
        await bridge.fetch_full_state()

    group_ids = {x.id for x in bridge.groups}
    scene = next(x for x in bridge.scenes.scene if x.group.rid in group_ids)

    assert bridge.scenes.scene.get_group(scene.id).id == scene.group.rid

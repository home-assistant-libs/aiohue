"""Test parsing of Scene.status field."""

import datetime
from unittest.mock import patch

from aiohue import HueBridgeV2
from aiohue.v2.models.scene import SceneActiveStatus


async def test_scene_status_parsing(v2_resources):
    """Ensure scene status (active + last_recall) is parsed correctly."""
    bridge = HueBridgeV2("127.0.0.1", "fake")

    with patch.object(bridge, "request", return_value=v2_resources):
        await bridge.fetch_full_state()

    # Collect scenes
    scenes = list(bridge.scenes.scene)  # regular scenes controller
    assert len(scenes) >= 2  # fixture contains at least two scenes

    dynamic_scene = scenes[0]
    static_scene = scenes[1]

    # dynamic scene assertions
    assert dynamic_scene.status is not None
    assert dynamic_scene.status.active == SceneActiveStatus.DYNAMIC_PALETTE
    assert isinstance(dynamic_scene.status.last_recall, datetime.datetime)

    # static scene assertions
    assert static_scene.status is not None
    assert static_scene.status.active == SceneActiveStatus.STATIC
    assert isinstance(static_scene.status.last_recall, datetime.datetime)

"""Test parsing of Scene.status field."""

import datetime
from unittest.mock import patch

from aiohue import HueBridgeV2
from aiohue.util import dataclass_from_dict
from aiohue.v2.models.scene import SceneActiveStatus, SceneStatus


async def test_scene_status_parsing(v2_resources):
    """Ensure scene status (active + last_recall) is parsed correctly."""
    bridge = HueBridgeV2("127.0.0.1", "fake")

    with patch.object(bridge, "request", return_value=v2_resources):
        await bridge.fetch_full_state()

    scenes = list(bridge.scenes.scene)  # regular scenes controller
    assert len(scenes) >= 2  # fixture contains at least two scenes

    def scene_with_status(active: SceneActiveStatus):
        return next(
            (x for x in scenes if x.status is not None and x.status.active == active),
            None,
        )

    dynamic_scene = scene_with_status(SceneActiveStatus.DYNAMIC_PALETTE)
    static_scene = scene_with_status(SceneActiveStatus.STATIC)

    assert dynamic_scene is not None
    assert isinstance(dynamic_scene.status.last_recall, datetime.datetime)

    assert static_scene is not None
    assert isinstance(static_scene.status.last_recall, datetime.datetime)


def test_scene_status_without_last_recall():
    """Ensure a scene that has never been recalled is parsed."""
    status = dataclass_from_dict(SceneStatus, {"active": "inactive"})

    assert status.active == SceneActiveStatus.INACTIVE
    assert status.last_recall is None

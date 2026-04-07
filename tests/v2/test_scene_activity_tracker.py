"""Tests for SceneActivityTracker."""

from unittest.mock import Mock, patch
from uuid import uuid4

from aiohue import HueBridgeV2
from aiohue.v2.controllers.events import EventType
from aiohue.v2.models.scene import SceneActiveStatus
from aiohue.v2.scene_activity import SceneActivityTracker


def _scene_data(
    scene_id: str,
    group_id: str,
    name: str,
    active: str,
    brightness: float | None = None,
) -> dict:
    """Build a minimal scene event data dict."""
    actions = []
    if brightness is not None:
        actions = [
            {
                "target": {"rid": str(uuid4()), "rtype": "light"},
                "action": {"dimming": {"brightness": brightness}},
            }
        ]
    return {
        "id": scene_id,
        "type": "scene",
        "metadata": {"name": name},
        "group": {"rid": group_id, "rtype": "room"},
        "actions": actions,
        "speed": 0.5,
        "status": {"active": active},
    }


def _smart_scene_data(scene_id: str, group_id: str, name: str, state: str) -> dict:
    """Build a minimal smart scene event data dict."""
    return {
        "id": scene_id,
        "type": "smart_scene",
        "metadata": {"name": name},
        "group": {"rid": group_id, "rtype": "room"},
        "week_timeslots": [],
        "state": state,
    }


async def test_active_scene_sets_state() -> None:
    """After a scene becomes active, group state reflects name and mode."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    scene_id = str(uuid4())
    group_id = str(uuid4())

    # pylint: disable=protected-access
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_ADDED,
        _scene_data(scene_id, group_id, "Relax", "inactive"),
    )

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_UPDATED,
        {"id": scene_id, "type": "scene", "status": {"active": "static"}},
    )

    state = tracker.get_group_state(group_id)
    assert state.active_scene_id == scene_id
    assert state.active_scene_name == "Relax"
    assert state.active_scene_mode == "static"


async def test_inactive_scene_clears_state() -> None:
    """When the tracked scene becomes inactive, group state is cleared."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    scene_id = str(uuid4())
    group_id = str(uuid4())

    # pylint: disable=protected-access
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_ADDED,
        _scene_data(scene_id, group_id, "Relax", "static"),
    )

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    # scene is now tracked as active; make it inactive
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_UPDATED,
        {"id": scene_id, "type": "scene", "status": {"active": "inactive"}},
    )

    state = tracker.get_group_state(group_id)
    assert state.active_scene_id is None
    assert state.active_scene_name is None
    assert state.active_scene_mode is None


async def test_inactive_event_for_untracked_scene_ignored() -> None:
    """An inactive update for a scene not currently tracked does not change state."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    scene_a = str(uuid4())
    scene_b = str(uuid4())
    group_id = str(uuid4())

    # pylint: disable=protected-access
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_ADDED,
        _scene_data(scene_a, group_id, "Relax", "static"),
    )
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_ADDED,
        _scene_data(scene_b, group_id, "Energize", "inactive"),
    )

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    # scene_a is active; fire inactive event for scene_b (not tracked)
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_UPDATED,
        {"id": scene_b, "type": "scene", "status": {"active": "inactive"}},
    )

    state = tracker.get_group_state(group_id)
    assert state.active_scene_id == scene_a
    assert state.active_scene_name == "Relax"


async def test_listener_called_on_update() -> None:
    """A subscribed listener is called with the group_id when state changes."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    scene_id = str(uuid4())
    group_id = str(uuid4())

    # pylint: disable=protected-access
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_ADDED,
        _scene_data(scene_id, group_id, "Relax", "inactive"),
    )

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    listener = Mock()
    tracker.subscribe(group_id, listener)

    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_UPDATED,
        {"id": scene_id, "type": "scene", "status": {"active": "static"}},
    )

    listener.assert_called_once_with(group_id)


async def test_listener_unsubscribe() -> None:
    """After unsubscribing, the listener is no longer called."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    scene_id = str(uuid4())
    group_id = str(uuid4())

    # pylint: disable=protected-access
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_ADDED,
        _scene_data(scene_id, group_id, "Relax", "inactive"),
    )

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    listener = Mock()
    unsubscribe = tracker.subscribe(group_id, listener)
    unsubscribe()

    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_UPDATED,
        {"id": scene_id, "type": "scene", "status": {"active": "static"}},
    )

    listener.assert_not_called()


async def test_active_smart_scene_sets_state() -> None:
    """When a smart scene becomes active, group state reflects its name."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    scene_id = str(uuid4())
    group_id = str(uuid4())

    # pylint: disable=protected-access
    await bridge.scenes.smart_scene._handle_event(
        EventType.RESOURCE_ADDED,
        _smart_scene_data(scene_id, group_id, "Morning", "inactive"),
    )

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    await bridge.scenes.smart_scene._handle_event(
        EventType.RESOURCE_UPDATED,
        {"id": scene_id, "type": "smart_scene", "state": "active"},
    )

    state = tracker.get_group_state(group_id)
    assert state.active_smart_scene_id == scene_id
    assert state.active_smart_scene_name == "Morning"


async def test_inactive_smart_scene_clears_state() -> None:
    """When the tracked smart scene becomes inactive, its state is cleared."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    scene_id = str(uuid4())
    group_id = str(uuid4())

    # pylint: disable=protected-access
    await bridge.scenes.smart_scene._handle_event(
        EventType.RESOURCE_ADDED,
        _smart_scene_data(scene_id, group_id, "Morning", "active"),
    )

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    await bridge.scenes.smart_scene._handle_event(
        EventType.RESOURCE_UPDATED,
        {"id": scene_id, "type": "smart_scene", "state": "inactive"},
    )

    state = tracker.get_group_state(group_id)
    assert state.active_smart_scene_id is None
    assert state.active_smart_scene_name is None


async def test_start_seeds_initial_state(v2_resources) -> None:
    """start() picks up already-active scenes from the controller."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    with patch.object(bridge, "request", return_value=v2_resources):
        await bridge.fetch_full_state()

    active_scenes = [
        s
        for s in bridge.scenes.scene
        if s.status and s.status.active != SceneActiveStatus.INACTIVE
    ]
    assert len(active_scenes) > 0, "fixture must contain at least one active scene"

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    for scene in active_scenes:
        state = tracker.get_group_state(scene.group.rid)
        assert state.active_scene_name == scene.metadata.name


async def test_stop_unsubscribes() -> None:
    """After stop(), scene events no longer update group state or call listeners."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    scene_id = str(uuid4())
    group_id = str(uuid4())

    # pylint: disable=protected-access
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_ADDED,
        _scene_data(scene_id, group_id, "Relax", "inactive"),
    )

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    listener = Mock()
    tracker.subscribe(group_id, listener)

    tracker.stop()

    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_UPDATED,
        {"id": scene_id, "type": "scene", "status": {"active": "static"}},
    )

    listener.assert_not_called()
    assert tracker.get_group_state(group_id).active_scene_id is None


async def test_dynamic_palette_mode() -> None:
    """A dynamic_palette active status is reflected in active_scene_mode."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    scene_id = str(uuid4())
    group_id = str(uuid4())

    # pylint: disable=protected-access
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_ADDED,
        _scene_data(scene_id, group_id, "Aurora", "inactive"),
    )

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_UPDATED,
        {
            "id": scene_id,
            "type": "scene",
            "status": {"active": "dynamic_palette"},
        },
    )

    state = tracker.get_group_state(group_id)
    assert state.active_scene_mode == "dynamic_palette"


async def test_brightness_extracted_from_actions() -> None:
    """Brightness is read from the first action with a dimming field."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    scene_id = str(uuid4())
    group_id = str(uuid4())

    # pylint: disable=protected-access
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_ADDED,
        _scene_data(scene_id, group_id, "Bright", "static", brightness=80.0),
    )

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    state = tracker.get_group_state(group_id)
    assert state.active_scene_brightness == 80.0


async def test_brightness_none_when_no_dimming_action() -> None:
    """Brightness is None when no scene action has a dimming field."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    scene_id = str(uuid4())
    group_id = str(uuid4())

    # pylint: disable=protected-access
    await bridge.scenes.scene._handle_event(
        EventType.RESOURCE_ADDED,
        _scene_data(scene_id, group_id, "No Dimming", "static", brightness=None),
    )

    tracker = SceneActivityTracker(bridge.scenes)
    tracker.start()

    state = tracker.get_group_state(group_id)
    assert state.active_scene_brightness is None

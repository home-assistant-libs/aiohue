"""Track active scene per Hue group (room/zone)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from aiohue.v2.models.scene import Scene, SceneActiveStatus
from aiohue.v2.models.smart_scene import SmartScene, SmartSceneState

if TYPE_CHECKING:
    from aiohue.v2.controllers.scenes import ScenesController

UpdateListener = Callable[[str], None]


@dataclass(slots=True)
class GroupSceneState:
    """Holds active scene data for a Hue group (room/zone)."""

    # Regular scene state
    active_scene_id: str | None = None
    active_scene_name: str | None = None
    active_scene_mode: str | None = None  # "static" | "dynamic_palette"
    active_scene_last_recall: datetime | None = None
    active_scene_speed: float | None = None  # 0.0–1.0 when dynamic palette active
    active_scene_brightness: float | None = None  # 0.0–100.0

    # Smart scene state
    active_smart_scene_id: str | None = None
    active_smart_scene_name: str | None = None


class SceneActivityTracker:
    """Track active (smart) scenes per Hue group and dispatch updates."""

    def __init__(self, scenes: ScenesController) -> None:
        """Initialize the tracker."""
        self._scenes = scenes
        self._group_states: dict[str, GroupSceneState] = defaultdict(GroupSceneState)
        self._listeners: dict[str, list[UpdateListener]] = defaultdict(list)
        self._unsub: Callable[[], None] | None = None

    def start(self) -> None:
        """Subscribe to scene events and seed initial state (idempotent)."""
        if self._unsub is not None:
            return

        def _handle_scene_event(
            event_type: object, scene: Scene | SmartScene
        ) -> None:
            if self._apply_scene_update(scene):
                group_id = scene.group.rid
                for listener in list(self._listeners[group_id]):
                    listener(group_id)

        self._unsub = self._scenes.subscribe(_handle_scene_event)

        updated_group_ids: set[str] = set()
        for smart_scene in self._scenes.smart_scene:
            if self._apply_scene_update(smart_scene):
                updated_group_ids.add(smart_scene.group.rid)
        for scene in self._scenes.scene:
            if self._apply_scene_update(scene):
                updated_group_ids.add(scene.group.rid)
        for group_id in updated_group_ids:
            for listener in list(self._listeners.get(group_id, [])):
                listener(group_id)

    def stop(self) -> None:
        """Stop listening to scene events."""
        if self._unsub:
            self._unsub()
            self._unsub = None

    def get_group_state(self, group_id: str) -> GroupSceneState:
        """Return (and lazily create) the state holder for a group."""
        return self._group_states[group_id]

    def subscribe(
        self, group_id: str, listener: UpdateListener
    ) -> Callable[[], None]:
        """Register a listener for a group; return an unsubscribe callable."""
        self._listeners[group_id].append(listener)

        def _remove() -> None:
            self._listeners[group_id].remove(listener)

        return _remove

    def _apply_scene_update(self, scene: Scene | SmartScene) -> bool:
        """Apply scene state to group tracking. Returns True if state changed."""
        if not scene.id:
            return False
        group_state = self._group_states[scene.group.rid]
        if isinstance(scene, Scene):
            return self._apply_regular_scene_update(scene, group_state)
        if isinstance(scene, SmartScene):
            return self._apply_smart_scene_update(scene, group_state)
        return False

    def _apply_regular_scene_update(
        self, scene: Scene, group_state: GroupSceneState
    ) -> bool:
        """Update group state from a regular scene event. Returns True if changed."""
        if scene.status is None:
            return False
        if scene.status.active != SceneActiveStatus.INACTIVE:
            group_state.active_scene_id = scene.id
            group_state.active_scene_name = scene.metadata.name
            group_state.active_scene_mode = scene.status.active.value
            group_state.active_scene_last_recall = scene.status.last_recall
            group_state.active_scene_speed = scene.speed
            group_state.active_scene_brightness = next(
                (
                    action.action.dimming.brightness
                    for action in scene.actions
                    if action.action.dimming is not None
                ),
                None,
            )
            return True
        if group_state.active_scene_id == scene.id:
            group_state.active_scene_id = None
            group_state.active_scene_name = None
            group_state.active_scene_mode = None
            group_state.active_scene_last_recall = None
            group_state.active_scene_speed = None
            group_state.active_scene_brightness = None
            return True
        return False

    def _apply_smart_scene_update(
        self, scene: SmartScene, group_state: GroupSceneState
    ) -> bool:
        """Update group state from a smart scene event. Returns True if changed."""
        if scene.state == SmartSceneState.ACTIVE:
            group_state.active_smart_scene_id = scene.id
            group_state.active_smart_scene_name = scene.metadata.name
            return True
        if group_state.active_smart_scene_id == scene.id:
            group_state.active_smart_scene_id = None
            group_state.active_smart_scene_name = None
            return True
        return False

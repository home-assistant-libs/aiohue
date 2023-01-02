"""Controller holding and managing HUE resources of type `scene`."""
from typing import TYPE_CHECKING, Optional, Type, Union

from ..models.feature import DimmingFeaturePut, RecallAction, RecallFeature
from ..models.resource import ResourceTypes
from ..models.room import Room
from ..models.scene import Scene, ScenePut
from ..models.smart_scene import (
    SmartScene,
    SmartScenePut,
    SmartSceneRecall,
    SmartSceneRecallAction,
)
from ..models.zone import Zone
from .base import BaseResourcesController, GroupedControllerBase

if TYPE_CHECKING:
    from .. import HueBridgeV2

SCENE_TYPES = Union[Scene, SmartScene]


class RegularScenesController(BaseResourcesController[Type[Scene]]):
    """Controller holding and managing HUE resources of type `scene`."""

    item_type = ResourceTypes.SCENE
    item_cls = Scene
    allow_parser_error = True

    async def recall(
        self,
        id: str,
        dynamic: bool = False,
        duration: Optional[int] = None,
        brightness: Optional[float] = None,
    ) -> None:
        """Turn on / recall scene."""
        action = RecallAction.DYNAMIC_PALETTE if dynamic else RecallAction.ACTIVE
        update_obj = ScenePut(recall=RecallFeature(action=action, duration=duration))
        if brightness is not None:
            update_obj.recall.dimming = DimmingFeaturePut(brightness=brightness)
        await self.update(id, update_obj)

    def get_group(self, id: str) -> Union[Room, Zone]:
        """Get group attached to given scene id."""
        scene = self[id]
        return next((x for x in self._bridge.groups if x.id == scene.group.rid))


class SmartScenesController(BaseResourcesController[Type[SmartScene]]):
    """Controller holding and managing HUE resources of type `smart_scene`."""

    item_type = ResourceTypes.SMART_SCENE
    item_cls = SmartScene
    allow_parser_error = False

    async def recall(
        self, id: str, action: SmartSceneRecallAction = SmartSceneRecallAction.ACTIVATE
    ) -> None:
        """Turn on / recall scene."""
        update_obj = SmartScenePut(recall=SmartSceneRecall(action=action))
        await self.update(id, update_obj)

    def get_group(self, id: str) -> Union[Room, Zone]:
        """Get group attached to given scene id."""
        scene = self[id]
        return next((x for x in self._bridge.groups if x.id == scene.group.rid))


class ScenesController(GroupedControllerBase[SCENE_TYPES]):
    """Controller grouping resources of all sensor resources."""

    def __init__(self, bridge: "HueBridgeV2") -> None:
        """Initialize instance."""
        self.scene = RegularScenesController(bridge)
        self.smart_scene = SmartScenesController(bridge)
        super().__init__(
            bridge,
            [
                self.scene,
                self.smart_scene,
            ],
        )

    async def recall(self, id: str, *args, **kwargs) -> None:
        """Turn on / recall scene."""
        scene = self[id]
        # forward call to correct controller
        # this method is here for convenience (and backwards compatibility)
        if isinstance(scene, SmartScene):
            await self.smart_scene.recall(id, *args, **kwargs)
            return
        await self.scene.recall(id, *args, **kwargs)

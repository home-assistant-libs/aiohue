"""Controller holding and managing HUE resources of type `scene`."""
from typing import Optional, Type, Union

from ..models.feature import DimmingFeaturePut, RecallAction, RecallFeature
from ..models.resource import ResourceTypes
from ..models.room import Room
from ..models.scene import Scene, ScenePut
from ..models.zone import Zone
from .base import BaseResourcesController


class ScenesController(BaseResourcesController[Type[Scene]]):
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

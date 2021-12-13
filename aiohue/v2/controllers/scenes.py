"""Controller holding and managing HUE resources of type `scene`."""
from __future__ import annotations

from typing import Type
from aiohue.v2.models.room import Room

from aiohue.v2.models.zone import Zone

from ..models.feature import RecallAction, RecallFeature

from ..models.resource import ResourceTypes
from ..models.scene import Scene
from .base import BaseResourcesController


class ScenesController(BaseResourcesController[Type[Scene]]):
    """Controller holding and managing HUE resources of type `scene`."""

    item_type = ResourceTypes.SCENE

    async def recall(
        self, id: str, dynamic: bool = False, duration: int | None = None
    ) -> None:
        """Turn on / recall scene."""
        action = RecallAction.DYNAMIC_PALETTE if dynamic else RecallAction.ACTIVE
        update_obj = Scene(
            id=id, recall=RecallFeature(action=action, duration=duration)
        )
        await self._send_put(id, update_obj)

    def get_group(self, id: str) -> Zone | Room:
        """Get group attached to given scene id."""
        scene = self[id]
        return next((x for x in self._bridge.groups if x.id == scene.group.rid))

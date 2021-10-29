"""Controller holding and managing HUE resources of type `scene`."""

from typing import Type

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

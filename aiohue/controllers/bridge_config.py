"""Controller holding and managing HUE resources of type `bridge`."""

from typing import Type

from ..models.bridge import Bridge
from ..models.resource import ResourceTypes
from .base import BaseResourcesController


class BridgeConfigController(BaseResourcesController[Type[Bridge]]):
    """Controller holding and managing HUE resources of type `bridge`."""

    item_type = ResourceTypes.BRIDGE

    @property
    def id(self) -> str | None:
        """Return id of the only/first bridge found in items."""
        for item in self.items:
            return item.id
        return None

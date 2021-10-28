"""Controller holding and managing HUE resources of type `scene`."""

from typing import Type

from ..models.resource import ResourceTypes
from ..models.scene import Scene
from .base import BaseResourcesController


class ScenesController(BaseResourcesController[Type[Scene]]):
    """Controller holding and managing HUE resources of type `scene`."""

    item_type = ResourceTypes.SCENE

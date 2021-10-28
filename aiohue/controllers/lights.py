"""Controller holding and managing HUE resources of type `light`."""

from typing import Type

from ..models.light import Light
from ..models.resource import ResourceTypes
from .base import BaseResourcesController


class LightsController(BaseResourcesController[Type[Light]]):
    """Controller holding and managing HUE resources of type `light`."""

    item_type = ResourceTypes.LIGHT

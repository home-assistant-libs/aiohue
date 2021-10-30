"""Controller holding and managing HUE resources of type `device`."""

from typing import List, Type

from ..models.light import Light
from ..models.room import Room

from ..models.resource import ResourceTypes
from ..models.device import Device
from .base import BaseResourcesController
from .sensors import SENSOR_TYPES


class DevicesController(BaseResourcesController[Type[Device]]):
    """Controller holding and managing HUE resources of type `device`."""

    item_type = ResourceTypes.DEVICE

    def get_lights(self, id: str) -> List[Light]:
        """Return all lights belonging to this device."""
        return [self._bridge.lights[x] for x in self[id].lights]

    def get_sensors(self, id: str) -> List[SENSOR_TYPES]:
        """Return all sensors belonging to this device."""
        return [self._bridge.sensors[x] for x in self[id].sensors]

    def get_room(self, id: str) -> Room | None:
        """Return room this device belongs to (if any)."""
        return next((x for x in self._bridge.groups.room if id in x.devices), None)

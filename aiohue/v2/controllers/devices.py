"""Controller holding and managing HUE resources of type `device`."""
from __future__ import annotations

from typing import List, Type

from ..models.connectivity import ZigbeeConnectivity
from ..models.device import Device
from ..models.light import Light
from ..models.resource import ResourceTypes
from ..models.room import Room
from .base import BaseResourcesController
from .sensors import SENSOR_TYPES


class DevicesController(BaseResourcesController[Type[Device]]):
    """Controller holding and managing HUE resources of type `device`."""

    item_type = ResourceTypes.DEVICE

    def get_lights(self, id: str) -> List[Light]:
        """Return all lights belonging to given device."""
        return [
            self._bridge.lights[x] for x in self[id].lights if x in self._bridge.lights
        ]

    def get_sensors(self, id: str) -> List[SENSOR_TYPES]:
        """Return all sensors belonging to given device."""
        return [
            self._bridge.sensors[x]
            for x in self[id].sensors
            if x in self._bridge.sensors
        ]

    def get_room(self, id: str) -> Room | None:
        """Return room the given device belongs to (if any)."""
        return next((x for x in self._bridge.groups.room if id in x.devices), None)

    def get_zigbee_connectivity(self, id: str) -> ZigbeeConnectivity | None:
        """Return the ZigbeeConnectivity resource connected to device."""
        for service in self._items[id].services:
            if service.rtype == ResourceTypes.ZIGBEE_CONNECTIVITY:
                return self._bridge.sensors.zigbee_connectivity[service.rid]
        return None

"""Controller holding and managing HUE resources of type `device`."""

from aiohue.v2.models.device import Device, DevicePut
from aiohue.v2.models.feature import IdentifyFeature
from aiohue.v2.models.light import Light
from aiohue.v2.models.resource import ResourceTypes
from aiohue.v2.models.room import Room
from aiohue.v2.models.zigbee_connectivity import ZigbeeConnectivity

from .base import BaseResourcesController
from .sensors import SENSOR_TYPES


class DevicesController(BaseResourcesController[type[Device]]):
    """Controller holding and managing HUE resources of type `device`."""

    item_type = ResourceTypes.DEVICE
    item_cls = Device

    def get_lights(self, id: str) -> list[Light]:
        """Return all lights belonging to given device."""
        return [x for x in self._bridge.lights if x.id in self[id].lights]

    def get_sensors(self, id: str) -> list[SENSOR_TYPES]:
        """Return all sensors belonging to given device."""
        return [x for x in self._bridge.sensors if x.id in self[id].sensors]

    def get_room(self, id: str) -> Room | None:
        """Return room the given device belongs to (if any)."""
        return next((x for x in self._bridge.groups.room if id in x.devices), None)

    def get_zigbee_connectivity(self, id: str) -> ZigbeeConnectivity | None:
        """Return the ZigbeeConnectivity resource connected to device."""
        for service in self._items[id].services:
            if service.rtype == ResourceTypes.ZIGBEE_CONNECTIVITY:
                return self._bridge.sensors.zigbee_connectivity.get(service.rid)
        return None

    async def set_identify(self, id: str) -> None:
        """
        Send identify command to the device.

        Triggers a visual identification sequence, current implemented as
        (which can change in the future):
        - Bridge performs Zigbee LED identification cycles for 5 seconds
        - Lights perform one breathe cycle
        - Sensors perform LED identification cycles for 15 seconds
        """
        await self.update(id, DevicePut(identify=IdentifyFeature()))

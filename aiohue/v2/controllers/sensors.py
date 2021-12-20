"""Controller holding and managing HUE resources of sensor type."""
from __future__ import annotations

from typing import TYPE_CHECKING, Type, Union

from ..models.connectivity import ZigbeeConnectivity
from ..models.device_power import DevicePower
from ..models.geofence_client import GeofenceClient
from ..models.light_level import LightLevel
from ..models.temperature import Temperature

from ..models.button import Button
from ..models.motion import Motion
from ..models.resource import ResourceTypes
from .base import BaseResourcesController, GroupedControllerBase

if TYPE_CHECKING:
    from .. import HueBridgeV2

SENSOR_TYPES = Union[
    DevicePower,
    Button,
    GeofenceClient,
    LightLevel,
    Motion,
    Temperature,
    ZigbeeConnectivity,
]


class DevicePowerController(BaseResourcesController[Type[DevicePower]]):
    """Controller holding and managing HUE resources of type `device_power`."""

    item_type = ResourceTypes.DEVICE_POWER


class ButtonController(BaseResourcesController[Type[Button]]):
    """Controller holding and managing HUE resources of type `button`."""

    item_type = ResourceTypes.BUTTON


class GeofenceClientController(BaseResourcesController[Type[GeofenceClient]]):
    """Controller holding and managing HUE resources of type `geofence_client`."""

    item_type = ResourceTypes.GEOFENCE_CLIENT


class LightLevelController(BaseResourcesController[Type[LightLevel]]):
    """Controller holding and managing HUE resources of type `light_level`."""

    item_type = ResourceTypes.LIGHT_LEVEL

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, LightLevel(id=id, enabled=enabled))


class MotionController(BaseResourcesController[Type[Motion]]):
    """Controller holding and managing HUE resources of type `motion`."""

    item_type = ResourceTypes.MOTION

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, Motion(id=id, enabled=enabled))


class TemperatureController(BaseResourcesController[Type[Temperature]]):
    """Controller holding and managing HUE resources of type `temperature`."""

    item_type = ResourceTypes.TEMPERATURE


class ZigbeeConnectivityController(BaseResourcesController[Type[ZigbeeConnectivity]]):
    """Controller holding and managing HUE resources of type `zigbee_connectivity`."""

    item_type = ResourceTypes.ZIGBEE_CONNECTIVITY


class SensorsController(GroupedControllerBase[SENSOR_TYPES]):
    """Controller grouping resources of all sensor resources."""

    def __init__(self, bridge: "HueBridgeV2") -> None:
        """Initialize instance."""
        self.button = ButtonController(bridge)
        self.device_power = DevicePowerController(bridge)
        self.geofence_client = GeofenceClientController(bridge)
        self.light_level = LightLevelController(bridge)
        self.motion = MotionController(bridge)
        self.temperature = TemperatureController(bridge)
        self.zigbee_connectivity = ZigbeeConnectivityController(bridge)
        super().__init__(
            bridge,
            [
                self.button,
                self.device_power,
                self.geofence_client,
                self.light_level,
                self.motion,
                self.temperature,
                self.zigbee_connectivity,
            ],
        )

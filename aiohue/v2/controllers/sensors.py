"""Controller holding and managing HUE resources of sensor type."""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Dict, Type, Union

from ..models.button import Button, ButtonEvent
from ..models.connectivity import ZigbeeConnectivity
from ..models.device_power import DevicePower
from ..models.geofence_client import GeofenceClient
from ..models.light_level import LightLevel
from ..models.motion import Motion
from ..models.resource import ResourceTypes
from ..models.temperature import Temperature
from .base import BaseResourcesController, GroupedControllerBase
from .events import EventType

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

BTN_WORKAROUND_NEEDED = ("FOHSWITCH",)


class DevicePowerController(BaseResourcesController[Type[DevicePower]]):
    """Controller holding and managing HUE resources of type `device_power`."""

    item_type = ResourceTypes.DEVICE_POWER


class ButtonController(BaseResourcesController[Type[Button]]):
    """Controller holding and managing HUE resources of type `button`."""

    item_type = ResourceTypes.BUTTON

    _workaround_tasks: Dict[str, asyncio.Task] = {}

    async def _handle_event(self, type: EventType, item: Button | None) -> None:
        """Handle incoming event for this resource from the EventStream."""
        await super()._handle_event(type, item)

        # Handle longpress workaround if needed
        if (
            not item
            or type != EventType.RESOURCE_UPDATED
            or not item.button
            or item.button.last_event != ButtonEvent.INITIAL_PRESS
        ):
            return

        device = self.get_device(item.id)
        if device is None or device.product_data.model_id not in BTN_WORKAROUND_NEEDED:
            return

        if item.id in self._workaround_tasks:
            # cancel existing task (if any)
            # should not happen, but just in case
            task = self._workaround_tasks.pop(item.id)
            if not task.done():
                task.cancel()

        self._workaround_tasks[item.id] = asyncio.create_task(
            self._handle_longpress_workaround(item.id)
        )

    async def _handle_longpress_workaround(self, id: int):
        """Handle workaround for FOH switches."""
        # Fake `held down` and `long press release` events.
        # This might need to be removed in a future release once/if Signify
        # adds this back in their API.
        await asyncio.sleep(1.5)  # time to initially wait for SHORT_RELEASE
        count = 0
        try:
            while count <= 20:  # = max 10 seconds
                btn_resource = self._items[id]
                cur_event = btn_resource.button.last_event
                if cur_event == ButtonEvent.SHORT_RELEASE:
                    break
                # send REPEAT until short release is received
                btn_resource.button.last_event = ButtonEvent.REPEAT
                await self._handle_event(EventType.RESOURCE_UPDATED, btn_resource)
                await asyncio.sleep(0.5)
                count += 1
        finally:
            # Fire LONG_RELEASE event if time between INITIAL_PRESS and SHORT_RELEASE
            # is more than 1.5 seconds or 10 seconds expired.
            # The button will not send SHORT_RELEASE if more than 10 seconds passed.
            # Note that the button will also fire the SHORT_RELEASE event if it's released within
            # those 10 seconds.
            if count > 1:
                btn_resource = self._items[id]
                btn_resource.button.last_event = ButtonEvent.LONG_RELEASE
                await self._handle_event(EventType.RESOURCE_UPDATED, btn_resource)


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

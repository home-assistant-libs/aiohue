"""Controller holding and managing HUE resources of sensor type."""
import asyncio
from typing import TYPE_CHECKING, Dict, Optional, Type, Union

from aiohue.util import dataclass_to_dict

from ..models.button import Button, ButtonEvent
from ..models.device_power import DevicePower
from ..models.geofence_client import GeofenceClient
from ..models.light_level import LightLevel, LightLevelPut
from ..models.motion import Motion, MotionPut
from ..models.resource import ResourceTypes
from ..models.temperature import Temperature
from ..models.zigbee_connectivity import ZigbeeConnectivity
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
    item_cls = DevicePower
    allow_parser_error = True


class ButtonController(BaseResourcesController[Type[Button]]):
    """Controller holding and managing HUE resources of type `button`."""

    item_type = ResourceTypes.BUTTON
    item_cls = Button
    allow_parser_error = True

    _workaround_tasks: Dict[str, asyncio.Task] = None

    async def _handle_event(
        self, evt_type: EventType, evt_data: Optional[dict], skip_forward: bool = False
    ) -> None:
        """Handle incoming event for this resource from the EventStream."""
        await super()._handle_event(evt_type, evt_data)

        # Handle longpress workaround if needed
        if (
            not evt_data
            or evt_type != EventType.RESOURCE_UPDATED
            or not evt_data.get("button")
            or evt_data["button"].get("last_event") != ButtonEvent.INITIAL_PRESS
        ):
            return

        device = self.get_device(evt_data["id"])
        if device is None or device.product_data.model_id not in BTN_WORKAROUND_NEEDED:
            return

        if self._workaround_tasks is None:
            self._workaround_tasks = {}

        if evt_data["id"] in self._workaround_tasks:
            # cancel existing task (if any)
            # should not happen, but just in case
            task = self._workaround_tasks.pop(evt_data["id"])
            if not task.done():
                task.cancel()

        self._workaround_tasks[evt_data["id"]] = asyncio.create_task(
            self._handle_longpress_workaround(evt_data["id"])
        )

    async def _handle_longpress_workaround(self, id: int):
        """Handle workaround for FOH switches."""
        # Fake `held down` and `long press release` events.
        # This might need to be removed in a future release once/if Signify
        # adds this back in their API.
        btn_resource = dataclass_to_dict(self._items[id])
        await asyncio.sleep(1.5)  # time to initially wait for SHORT_RELEASE
        count = 0
        try:
            while count <= 20:  # = max 10 seconds
                cur_event = self._items[id].button.last_event
                if cur_event == ButtonEvent.SHORT_RELEASE:
                    break
                # send REPEAT until short release is received
                btn_resource["button"]["last_event"] = ButtonEvent.REPEAT.value
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
                btn_resource["button"]["last_event"] = ButtonEvent.LONG_RELEASE.value
                await self._handle_event(EventType.RESOURCE_UPDATED, btn_resource)


class GeofenceClientController(BaseResourcesController[Type[GeofenceClient]]):
    """Controller holding and managing HUE resources of type `geofence_client`."""

    item_type = ResourceTypes.GEOFENCE_CLIENT
    item_cls = GeofenceClient
    allow_parser_error = True


class LightLevelController(BaseResourcesController[Type[LightLevel]]):
    """Controller holding and managing HUE resources of type `light_level`."""

    item_type = ResourceTypes.LIGHT_LEVEL
    item_cls = LightLevel
    allow_parser_error = True

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, LightLevelPut(enabled=enabled))


class MotionController(BaseResourcesController[Type[Motion]]):
    """Controller holding and managing HUE resources of type `motion`."""

    item_type = ResourceTypes.MOTION
    item_cls = Motion
    allow_parser_error = True

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, MotionPut(enabled=enabled))


class TemperatureController(BaseResourcesController[Type[Temperature]]):
    """Controller holding and managing HUE resources of type `temperature`."""

    item_type = ResourceTypes.TEMPERATURE
    item_cls = Temperature
    allow_parser_error = True


class ZigbeeConnectivityController(BaseResourcesController[Type[ZigbeeConnectivity]]):
    """Controller holding and managing HUE resources of type `zigbee_connectivity`."""

    item_type = ResourceTypes.ZIGBEE_CONNECTIVITY
    item_cls = ZigbeeConnectivity
    allow_parser_error = True


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

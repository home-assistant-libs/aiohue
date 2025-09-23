"""Controller holding and managing HUE resources of sensor type."""

import asyncio
from typing import TYPE_CHECKING

from aiohue.util import dataclass_to_dict
from aiohue.v2.models.bell_button import BellButton
from aiohue.v2.models.bridge_home import BridgeHome
from aiohue.v2.models.button import Button, ButtonEvent
from aiohue.v2.models.camera_motion import CameraMotion, CameraMotionPut
from aiohue.v2.models.contact import Contact, ContactPut
from aiohue.v2.models.convenience_area_motion import (
    ConvenienceAreaMotion,
    ConvenienceAreaMotionPut,
)
from aiohue.v2.models.device_power import DevicePower
from aiohue.v2.models.feature import MotionSensingFeatureSensitivityPut
from aiohue.v2.models.geofence_client import GeofenceClient
from aiohue.v2.models.grouped_light_level import GroupedLightLevel, GroupedLightLevelPut
from aiohue.v2.models.grouped_motion import GroupedMotion, GroupedMotionPut
from aiohue.v2.models.light_level import LightLevel, LightLevelPut
from aiohue.v2.models.motion import Motion, MotionPut
from aiohue.v2.models.motion_area_configuration import MotionAreaConfiguration
from aiohue.v2.models.relative_rotary import RelativeRotary
from aiohue.v2.models.resource import ResourceTypes
from aiohue.v2.models.room import Room
from aiohue.v2.models.security_area_motion import (
    SecurityAreaMotion,
    SecurityAreaMotionPut,
)
from aiohue.v2.models.service_group import ServiceGroup
from aiohue.v2.models.tamper import Tamper
from aiohue.v2.models.temperature import Temperature
from aiohue.v2.models.zigbee_connectivity import ZigbeeConnectivity
from aiohue.v2.models.zone import Zone

from .base import BaseResourcesController, GroupedControllerBase
from .events import EventType

if TYPE_CHECKING:
    from aiohue.v2 import HueBridgeV2

SENSOR_TYPES = (
    DevicePower
    | BellButton
    | Button
    | CameraMotion
    | Contact
    | ConvenienceAreaMotion
    | GeofenceClient
    | GroupedLightLevel
    | GroupedMotion
    | LightLevel
    | Motion
    | RelativeRotary
    | SecurityAreaMotion
    | Tamper
    | Temperature
    | ZigbeeConnectivity
)


BTN_WORKAROUND_NEEDED = ("FOHSWITCH",)


class DevicePowerController(BaseResourcesController[type[DevicePower]]):
    """Controller holding and managing HUE resources of type `device_power`."""

    item_type = ResourceTypes.DEVICE_POWER
    item_cls = DevicePower
    allow_parser_error = True


class BellButtonController(BaseResourcesController[type[BellButton]]):
    """Controller holding and managing HUE resources of type `bell_button`."""

    item_type = ResourceTypes.BELL_BUTTON
    item_cls = BellButton
    allow_parser_error = True


class ButtonController(BaseResourcesController[type[Button]]):
    """Controller holding and managing HUE resources of type `button`."""

    item_type = ResourceTypes.BUTTON
    item_cls = Button
    allow_parser_error = True

    _workaround_tasks: dict[str, asyncio.Task] = None

    async def _handle_event(
        self,
        evt_type: EventType,
        evt_data: dict | None,
        is_reconnect: bool = False,  # noqa: ARG002
    ) -> None:
        """Handle incoming event for this resource from the EventStream."""
        await super()._handle_event(evt_type, evt_data)

        if not evt_data:
            return

        # Handle longpress workaround if needed
        if not (
            evt_type == EventType.RESOURCE_UPDATED
            and evt_data.get("button", {}).get("button_report", {}).get("event")
            == ButtonEvent.INITIAL_PRESS.value
        ):
            return

        device = self.get_device(evt_data["id"])
        if device is None or device.product_data.model_id not in BTN_WORKAROUND_NEEDED:
            return

        if self._workaround_tasks is None:
            self._workaround_tasks = {}

        # cancel existing task (if any)
        # should not happen, but just in case
        task = self._workaround_tasks.pop(evt_data["id"], None)
        if task and not task.done():
            task.cancel()

        self._workaround_tasks[evt_data["id"]] = asyncio.create_task(
            self._handle_longpress_workaround(evt_data["id"])
        )

    async def _handle_longpress_workaround(self, id: int):
        """Handle workaround for FOH switches."""
        # Fake `held down` and `long press release` events.
        # This might need to be removed in a future release once/if Signify
        # adds this back in their API.
        self._logger.debug("Long press workaround for FOH switch initiated.")
        btn_resource = dataclass_to_dict(self._items[id])
        await asyncio.sleep(1.5)  # time to initially wait for SHORT_RELEASE
        count = 0
        try:
            while count <= 20:  # = max 10 seconds
                cur_event = self._items[id].button.button_report.event
                if cur_event == ButtonEvent.SHORT_RELEASE:
                    break
                # send REPEAT until short release is received
                btn_resource["button"]["button_report"]["event"] = (
                    ButtonEvent.REPEAT.value
                )
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
                btn_resource["button"]["button_report"]["event"] = (
                    ButtonEvent.LONG_RELEASE.value
                )
                await self._handle_event(EventType.RESOURCE_UPDATED, btn_resource)
            self._logger.debug("Long press workaround for FOH switch completed.")


class CameraMotionController(BaseResourcesController[type[CameraMotion]]):
    """Controller holding and managing HUE resources of type `camera_motion`."""

    item_type = ResourceTypes.CAMERA_MOTION
    item_cls = CameraMotion
    allow_parser_error = True

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, MotionPut(enabled=enabled))

    async def set_sensitivity(self, id: str, sensitivity: int) -> None:
        """Enable/Disable sensor."""
        await self.update(id, CameraMotionPut(sensitivity=sensitivity))


class ContactController(BaseResourcesController[type[Contact]]):
    """Controller holding and managing HUE resources of type `contact`."""

    item_type = ResourceTypes.CONTACT
    item_cls = Contact
    allow_parser_error = True

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, ContactPut(enabled=enabled))


class ConvenienceAreaMotionController(
    BaseResourcesController[type[ConvenienceAreaMotion]]
):
    """Controller holding and managing HUE resources of type `convenience_area_motion`."""

    item_type = ResourceTypes.CONVENIENCE_AREA_MOTION
    item_cls = ConvenienceAreaMotion
    allow_parser_error = True

    def get_motion_area_configuration(self, id: str) -> MotionAreaConfiguration:
        """Get the motion area configuration connected to convenience area motion."""
        for area_config in self._bridge.config.motion_area_configuration:
            for service in area_config.services:
                if service.rid == id:
                    return area_config
        raise KeyError(
            f"Motion area configuration for convenience area motion {id} not found"
        )

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, ConvenienceAreaMotionPut(enabled=enabled))

    async def set_sensitivity(self, id: str, sensitivity: int) -> None:
        """Set motion sensor sensitivity."""
        await self.update(
            id,
            ConvenienceAreaMotionPut(
                sensitivity=MotionSensingFeatureSensitivityPut(sensitivity=sensitivity)
            ),
        )


class SecurityAreaMotionController(BaseResourcesController[type[SecurityAreaMotion]]):
    """Controller holding and managing HUE resources of type `security_area_motion`."""

    item_type = ResourceTypes.SECURITY_AREA_MOTION
    item_cls = SecurityAreaMotion
    allow_parser_error = True

    def get_motion_area_configuration(self, id: str) -> MotionAreaConfiguration:
        """Get the motion area configuration connected to security area motion."""
        for area_config in self._bridge.config.motion_area_configuration:
            for service in area_config.services:
                if service.rid == id:
                    return area_config
        raise KeyError(
            f"Motion area configuration for security area motion {id} not found"
        )

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, SecurityAreaMotionPut(enabled=enabled))

    async def set_sensitivity(self, id: str, sensitivity: int) -> None:
        """Set motion sensor sensitivity."""
        await self.update(
            id,
            SecurityAreaMotionPut(
                sensitivity=MotionSensingFeatureSensitivityPut(sensitivity=sensitivity)
            ),
        )


class GeofenceClientController(BaseResourcesController[type[GeofenceClient]]):
    """Controller holding and managing HUE resources of type `geofence_client`."""

    item_type = ResourceTypes.GEOFENCE_CLIENT
    item_cls = GeofenceClient
    allow_parser_error = True


class GroupedLightLevelController(BaseResourcesController[type[GroupedLightLevel]]):
    """Controller holding and managing HUE resources of type `grouped_light_level`."""

    item_type = ResourceTypes.GROUPED_LIGHT_LEVEL
    item_cls = GroupedLightLevel
    allow_parser_error = True

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, GroupedLightLevelPut(enabled=enabled))


class GroupedMotionController(BaseResourcesController[type[GroupedMotion]]):
    """Controller holding and managing HUE resources of type `grouped_motion`."""

    item_type = ResourceTypes.GROUPED_MOTION
    item_cls = GroupedMotion
    allow_parser_error = True

    def get_parent(self, id: str) -> ServiceGroup | Room | Zone | BridgeHome | None:
        """Get the parent (ServiceGroup or Room/Zone) connected to grouped motion (if any)."""
        grouped_motion = self._items[id]
        if grouped_motion.owner.rtype == ResourceTypes.SERVICE_GROUP:
            return self._bridge.config.service_group[grouped_motion.owner.rid]
        if grouped_motion.owner.rtype == ResourceTypes.ROOM:
            return self._bridge.groups.room[grouped_motion.owner.rid]
        if grouped_motion.owner.rtype == ResourceTypes.ZONE:
            return self._bridge.groups.zone[grouped_motion.owner.rid]
        if grouped_motion.owner.rtype == ResourceTypes.BRIDGE_HOME:
            return self._bridge.config.bridge_home
        return None

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, GroupedMotionPut(enabled=enabled))


class LightLevelController(BaseResourcesController[type[LightLevel]]):
    """Controller holding and managing HUE resources of type `light_level`."""

    item_type = ResourceTypes.LIGHT_LEVEL
    item_cls = LightLevel
    allow_parser_error = True

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, LightLevelPut(enabled=enabled))


class MotionController(BaseResourcesController[type[Motion]]):
    """Controller holding and managing HUE resources of type `motion`."""

    item_type = ResourceTypes.MOTION
    item_cls = Motion
    allow_parser_error = True

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, MotionPut(enabled=enabled))


class RelativeRotaryController(BaseResourcesController[type[Button]]):
    """Controller holding and managing HUE resources of type `relative_rotary`."""

    item_type = ResourceTypes.RELATIVE_ROTARY
    item_cls = RelativeRotary
    allow_parser_error = True


class TamperController(BaseResourcesController[type[Tamper]]):
    """Controller holding and managing HUE resources of type `tamper`."""

    item_type = ResourceTypes.TAMPER
    item_cls = Tamper
    allow_parser_error = True


class TemperatureController(BaseResourcesController[type[Temperature]]):
    """Controller holding and managing HUE resources of type `temperature`."""

    item_type = ResourceTypes.TEMPERATURE
    item_cls = Temperature
    allow_parser_error = True


class ZigbeeConnectivityController(BaseResourcesController[type[ZigbeeConnectivity]]):
    """Controller holding and managing HUE resources of type `zigbee_connectivity`."""

    item_type = ResourceTypes.ZIGBEE_CONNECTIVITY
    item_cls = ZigbeeConnectivity
    allow_parser_error = True


class SensorsController(GroupedControllerBase[SENSOR_TYPES]):
    """Controller grouping resources of all sensor resources."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, bridge: "HueBridgeV2") -> None:
        """Initialize instance."""
        self.bell_button = BellButtonController(bridge)
        self.button = ButtonController(bridge)
        self.camera_motion = CameraMotionController(bridge)
        self.contact = ContactController(bridge)
        self.convenience_area_motion = ConvenienceAreaMotionController(bridge)
        self.device_power = DevicePowerController(bridge)
        self.geofence_client = GeofenceClientController(bridge)
        self.grouped_light_level = GroupedLightLevelController(bridge)
        self.grouped_motion = GroupedMotionController(bridge)
        self.light_level = LightLevelController(bridge)
        self.motion = MotionController(bridge)
        self.relative_rotary = RelativeRotaryController(bridge)
        self.security_area_motion = SecurityAreaMotionController(bridge)
        self.tamper = TamperController(bridge)
        self.temperature = TemperatureController(bridge)
        self.zigbee_connectivity = ZigbeeConnectivityController(bridge)
        super().__init__(
            bridge,
            [
                self.bell_button,
                self.button,
                self.camera_motion,
                self.contact,
                self.convenience_area_motion,
                self.device_power,
                self.geofence_client,
                self.grouped_light_level,
                self.grouped_motion,
                self.light_level,
                self.motion,
                self.relative_rotary,
                self.security_area_motion,
                self.tamper,
                self.temperature,
                self.zigbee_connectivity,
            ],
        )

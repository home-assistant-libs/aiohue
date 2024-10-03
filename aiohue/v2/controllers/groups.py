"""Controller holding and managing HUE group resources."""

import asyncio
from typing import TYPE_CHECKING, Union

from aiohue.v2.models.feature import (
    AlertEffectType,
    AlertFeaturePut,
    ColorFeaturePut,
    ColorPoint,
    ColorTemperatureFeaturePut,
    DeltaAction,
    DimmingFeaturePut,
    DimmingDeltaFeaturePut,
    DynamicsFeaturePut,
    OnFeature,
)
from aiohue.v2.models.grouped_light import GroupedLight, GroupedLightPut
from aiohue.v2.models.light import Light
from aiohue.v2.models.resource import ResourceTypes
from aiohue.v2.models.room import Room
from aiohue.v2.models.scene import Scene
from aiohue.v2.models.zone import Zone

from .base import BaseResourcesController, GroupedControllerBase

if TYPE_CHECKING:
    from aiohue.v2 import HueBridgeV2


class RoomController(BaseResourcesController[type[Room]]):
    """Controller holding and managing HUE resources of type `room`."""

    item_type = ResourceTypes.ROOM
    item_cls = Room
    allow_parser_error = True

    def get_scenes(self, id: str) -> list[Scene]:
        """Get all scenes for this room."""
        return [scene for scene in self._bridge.scenes if scene.group.rid == id]

    def get_lights(self, id: str) -> list[Light]:
        """Return all lights in given room."""
        if id not in self._items:
            return []
        result = []
        for dev_id in self._items[id].devices:
            if (dev := self._bridge.devices.get(dev_id)) is None:
                continue

            for light_id in dev.lights:
                if light := self._bridge.lights.get(light_id):
                    result.append(light)
        return result


class ZoneController(BaseResourcesController[type[Zone]]):
    """Controller holding and managing HUE resources of type `zone`."""

    item_type = ResourceTypes.ZONE
    item_cls = Zone
    allow_parser_error = True

    def get_scenes(self, id: str) -> list[Scene]:
        """Get all scenes for this room."""
        return [scene for scene in self._bridge.scenes if scene.group.rid == id]

    def get_lights(self, id: str) -> list[Light]:
        """Return all lights in given zone."""
        if id not in self._items:
            return []
        light_ids = {
            x.rid for x in self._items[id].children if x.rtype == ResourceTypes.LIGHT
        }
        return [x for x in self._bridge.lights if x.id in light_ids]


class GroupedLightController(BaseResourcesController[type[GroupedLight]]):
    """Controller holding and managing HUE resources of type `grouped_light`."""

    item_type = ResourceTypes.GROUPED_LIGHT
    item_cls = GroupedLight

    def get_zone(self, id: str) -> Room | Zone | None:
        """Get the zone or room connected to grouped light."""
        for group in self._bridge.groups:
            if group.type == ResourceTypes.GROUPED_LIGHT:
                continue
            if group.grouped_light == id:
                return group
        return None

    def get_lights(self, id: str) -> list[Light]:
        """Return lights of the connected room/zone."""
        # Note that this is just a convenience method for backwards compatibility
        if zone := self.get_zone(id):
            if zone.type == ResourceTypes.ROOM:
                return self._bridge.groups.room.get_lights(zone.id)
            return self._bridge.groups.zone.get_lights(zone.id)
        return []

    async def set_flash(self, id: str, short: bool = False) -> None:
        """Send Flash command to grouped_light."""
        if short:
            # redirect command to underlying lights
            await asyncio.gather(
                *[
                    self._bridge.lights.set_flash(
                        id=light.id,
                        short=True,
                    )
                    for light in self.get_lights(id)
                ]
            )
            return
        await self.set_state(id, alert=AlertEffectType.BREATHE)

    async def set_state(
        self,
        id: str,
        on: bool | None = None,
        brightness: float | None = None,
        color_xy: tuple[float, float] | None = None,
        color_temp: int | None = None,
        transition_time: int | None = None,
        alert: AlertEffectType | None = None,
    ) -> None:
        """Set supported feature(s) to grouped_light resource."""
        # Sending (color) commands to grouped_light was added in Bridge version 1.50.1950111030
        self._bridge.config.require_version("1.50.1950111030")
        update_obj = GroupedLightPut()
        if on is not None:
            update_obj.on = OnFeature(on=on)
        if brightness is not None:
            update_obj.dimming = DimmingFeaturePut(brightness=brightness)
        if color_xy is not None:
            update_obj.color = ColorFeaturePut(xy=ColorPoint(*color_xy))
        if color_temp is not None:
            update_obj.color_temperature = ColorTemperatureFeaturePut(mirek=color_temp)
        if transition_time is not None:
            update_obj.dynamics = DynamicsFeaturePut(duration=transition_time)
        if alert is not None:
            update_obj.alert = AlertFeaturePut(action=alert)

        await self.update(id, update_obj)

    async def set_dimming_delta(
        self, id: str, brightness_delta: float | None = None
    ) -> None:
        """
        Set brightness_delta value and action via DimmingDeltaFeature.

        The action to be send depends on brightness_delta value:
         None: STOP (this immediately stops any dimming transition)
         > 0: UP,
         < 0: DOWN
        """
        if brightness_delta in (None, 0):
            dimming_delta = DimmingDeltaFeaturePut(action=DeltaAction.STOP)
        else:
            dimming_delta = DimmingDeltaFeaturePut(
                action=DeltaAction.UP if brightness_delta > 0 else DeltaAction.DOWN,
                brightness_delta=abs(brightness_delta),
            )

        update_obj = GroupedLightPut()
        update_obj.dimming_delta = dimming_delta
        await self.update(id, update_obj)


class GroupsController(GroupedControllerBase[Union[Room, Zone, GroupedLight]]):  # noqa: UP007
    """Controller grouping resources of both room and zone."""

    def __init__(self, bridge: "HueBridgeV2") -> None:
        """Initialize instance."""
        self.grouped_light = GroupedLightController(bridge)
        self.room = RoomController(bridge)
        self.zone = ZoneController(bridge)
        super().__init__(
            bridge,
            [
                self.room,
                self.zone,
                self.grouped_light,
            ],
        )

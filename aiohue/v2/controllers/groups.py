"""Controller holding and managing HUE group resources."""
import asyncio
from typing import TYPE_CHECKING, List, Optional, Tuple, Type, Union

from ..models.feature import (
    AlertEffectType,
    AlertFeaturePut,
    ColorFeaturePut,
    ColorPoint,
    ColorTemperatureFeaturePut,
    DimmingFeaturePut,
    DynamicsFeaturePut,
    OnFeature,
)
from ..models.grouped_light import GroupedLight, GroupedLightPut
from ..models.light import Light
from ..models.resource import ResourceTypes
from ..models.room import Room
from ..models.scene import Scene
from ..models.zone import Zone
from .base import BaseResourcesController, GroupedControllerBase

if TYPE_CHECKING:
    from .. import HueBridgeV2


class RoomController(BaseResourcesController[Type[Room]]):
    """Controller holding and managing HUE resources of type `room`."""

    item_type = ResourceTypes.ROOM
    item_cls = Room
    allow_parser_error = True

    def get_scenes(self, id: str) -> List[Scene]:
        """Get all scenes for this room."""
        return [scene for scene in self._bridge.scenes if scene.group.rid == id]

    def get_lights(self, id: str) -> List[Light]:
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


class ZoneController(BaseResourcesController[Type[Zone]]):
    """Controller holding and managing HUE resources of type `zone`."""

    item_type = ResourceTypes.ZONE
    item_cls = Zone
    allow_parser_error = True

    def get_scenes(self, id: str) -> List[Scene]:
        """Get all scenes for this room."""
        return [scene for scene in self._bridge.scenes if scene.group.rid == id]

    def get_lights(self, id: str) -> List[Light]:
        """Return all lights in given zone."""
        if id not in self._items:
            return []
        light_ids = {
            x.rid for x in self._items[id].children if x.rtype == ResourceTypes.LIGHT
        }
        return [x for x in self._bridge.lights if x.id in light_ids]


class GroupedLightController(BaseResourcesController[Type[GroupedLight]]):
    """Controller holding and managing HUE resources of type `grouped_light`."""

    item_type = ResourceTypes.GROUPED_LIGHT
    item_cls = GroupedLight

    def get_zone(self, id: str) -> Union[Room, Zone, None]:
        """Get the zone or room connected to grouped light."""
        for group in self._bridge.groups:
            if group.type == ResourceTypes.GROUPED_LIGHT:
                continue
            if group.grouped_light == id:
                return group
        return None

    def get_lights(self, id: str) -> List[Light]:
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
        on: Optional[bool] = None,
        brightness: Optional[float] = None,
        color_xy: Optional[Tuple[float, float]] = None,
        color_temp: Optional[int] = None,
        transition_time: Optional[int] = None,
        alert: Optional[AlertEffectType] = None,
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


class GroupsController(GroupedControllerBase[Union[Room, Zone, GroupedLight]]):
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

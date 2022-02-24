"""Controller holding and managing HUE group resources."""
from typing import TYPE_CHECKING, List, Type, Union

from ..models.feature import OnFeature
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
            if dev := self._bridge.devices.get(dev_id):
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

    async def set_state(self, id: str, on: bool = True) -> None:
        """
        Set supported feature(s) to grouped_light resource.

        NOTE: a grouped_light can only handle OnFeature
        To send other features, you'll have to control the underlying lights
        """
        await self.update(id, GroupedLightPut(on=OnFeature(on=on)))


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

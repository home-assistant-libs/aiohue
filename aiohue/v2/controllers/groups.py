"""Controller holding and managing HUE group resources."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Type, Union

from ..models.feature import OnFeature
from ..models.group import Group
from ..models.grouped_light import GroupedLight
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

    def get_scenes(self, id: str) -> List[Scene]:
        """Get all scenes for this room."""
        return [scene for scene in self._bridge.scenes if scene.group.rid == id]


class ZoneController(BaseResourcesController[Type[Zone]]):
    """Controller holding and managing HUE resources of type `zone`."""

    item_type = ResourceTypes.ZONE

    def get_scenes(self, id: str) -> List[Scene]:
        """Get all scenes for this zone."""
        return [scene for scene in self._bridge.scenes if scene.group.rid == id]


class GroupedLightController(BaseResourcesController[Type[GroupedLight]]):
    """Controller holding and managing HUE resources of type `grouped_light`."""

    item_type = ResourceTypes.GROUPED_LIGHT

    def get_zone(self, id: str) -> Room | Zone | None:
        """Get the zone or room connected to grouped light."""
        for group in self._bridge.groups:
            if group.type == ResourceTypes.GROUPED_LIGHT:
                continue
            if group.grouped_light == id:
                return group
        return None

    def get_lights(self, id: str) -> List[Light]:
        """Return all underlying lights of this grouped light."""
        if zone := self.get_zone(id):
            return [self._bridge.lights[x] for x in zone.lights]
        return []  # fallback for a group without a zone (special 0 group)

    async def set_state(self, id: str, on: bool = True) -> None:
        """
        Set supported feature(s) to grouped_light resource.

        NOTE: a grouped_light can only handle OnFeature
        To send other features, you'll have to control the underlying lights
        """
        await self.update(id, GroupedLight(id, on=OnFeature(on=on)))


class GroupsController(GroupedControllerBase[Union[Room, Group, GroupedLight]]):
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

"""Controller holding and managing HUE resources of type `room`."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Type, Union

from aiohue.v2.models.light import Light

from ..models.clip import CLIPResource
from ..models.group import Group
from ..models.grouped_light import GroupedLight
from ..models.resource import ResourceTypes
from ..models.room import Room
from ..models.zone import Zone
from .base import BaseResourcesController, GroupedControllerBase
from .events import EventType

if TYPE_CHECKING:
    from .. import HueBridgeV2


class RoomController(BaseResourcesController[Type[Room]]):
    """Controller holding and managing HUE resources of type `room`."""

    item_type = ResourceTypes.ROOM

    def get_scenes(self, id: str):
        """Get all scenes for this room."""
        return [scene for scene in self._bridge.scenes if scene.group.rid == id]


class ZoneController(BaseResourcesController[Type[Zone]]):
    """Controller holding and managing HUE resources of type `zone`."""

    item_type = ResourceTypes.ZONE

    def get_scenes(self, id: str):
        """Get all scenes for this zone."""
        return [scene for scene in self._bridge.scenes if scene.group.rid == id]


class GroupedLightController(BaseResourcesController[Type[GroupedLight]]):
    """Controller holding and managing HUE resources of type `grouped_light`."""

    item_type = ResourceTypes.GROUPED_LIGHT

    async def _handle_event(self, type: EventType, item: CLIPResource) -> None:
        """Handle incoming event for this resource from the EventStream."""
        await super()._handle_event(type, item)
        # make sure that an update of grouped light gets propagated to connected zone/room
        if type != EventType.RESOURCE_UPDATED:
            return
        self._bridge.events.emit(EventType.RESOURCE_UPDATED, self.get_zone(item.id))

    def get_zone(self, id: str) -> Room | Zone:
        """Get the zone or room connected to grouped light."""
        for group in self._bridge.groups:
            if group.type == ResourceTypes.GROUPED_LIGHT:
                continue
            if group.grouped_light == id:
                return group

    def get_lights(self, id: str) -> List[Light]:
        """Return all underlying lights of this grouped light."""
        return [self._bridge.lights[x] for x in self.get_zone(id).lights]


class GroupsController(GroupedControllerBase[Union[Room, Group, GroupedLight]]):
    """Controller grouping resources of both room and zone."""

    def __init__(self, bridge: "HueBridgeV2") -> None:
        """Initialize instance."""
        self.room = RoomController(bridge)
        self.zone = ZoneController(bridge)
        self.grouped_light = GroupedLightController(bridge)
        super().__init__(
            bridge,
            [
                self.room,
                self.zone,
                self.grouped_light,
            ],
        )

"""Controller holding and managing HUE resources of type `room`."""

from typing import TYPE_CHECKING, Type, Union

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


class ZoneController(BaseResourcesController[Type[Zone]]):
    """Controller holding and managing HUE resources of type `zone`."""

    item_type = ResourceTypes.ZONE


class GroupedLightController(BaseResourcesController[Type[GroupedLight]]):
    """Controller holding and managing HUE resources of type `grouped_light`."""

    item_type = ResourceTypes.GROUPED_LIGHT

    async def _handle_event(self, type: EventType, item: CLIPResource) -> None:
        """Handle incoming event for this resource from the EventStream."""
        await super()._handle_event(type, item)
        # make sure that an update of grouped light gets propagated to connected zone/room
        self._bridge.events.emit(EventType.RESOURCE_UPDATED, self.get_zone(item.id))

    def get_zone(self, id: str) -> Room | Zone:
        """Get the zone or room connected to grouped light."""
        for group in self._bridge.groups:
            if group.type == ResourceTypes.GROUPED_LIGHT:
                continue
            if group.grouped_light == id:
                return group


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

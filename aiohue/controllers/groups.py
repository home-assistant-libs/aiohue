"""Controller holding and managing HUE resources of type `room`."""

from typing import TYPE_CHECKING, Type, Union

from ..models.group import Group
from ..models.grouped_light import GroupedLight
from ..models.resource import ResourceTypes
from ..models.room import Room
from ..models.zone import Zone
from .base import BaseResourcesController, GroupedControllerBase

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

"""Controller holding and managing HUE resources of type `room`."""
from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING, List, Optional, Tuple, Type, Union

from ...errors import AiohueException

from ..models.clip import CLIPResource
from ..models.feature import OnFeature
from ..models.group import Group
from ..models.grouped_light import GroupedLight
from ..models.light import Light
from ..models.resource import ResourceTypes
from ..models.room import Room
from ..models.scene import Scene
from ..models.zone import Zone
from .base import BaseResourcesController, GroupedControllerBase
from .events import EventType

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

    async def _handle_event(self, type: EventType, item: CLIPResource) -> None:
        """Handle incoming event for this resource from the EventStream."""
        await super()._handle_event(type, item)
        # make sure that an update of grouped light gets propagated to connected zone/room
        if type != EventType.RESOURCE_UPDATED:
            return
        if zone := self.get_zone(item.id):
            self._bridge.events.emit(EventType.RESOURCE_UPDATED, zone)

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

    async def set_state(
        self,
        id: str,
        on: bool = True,
        brightness: Optional[float] = None,
        color_xy: Optional[Tuple[float, float]] = None,
        color_temp: Optional[int] = None,
        transition_time: int | None = None,
    ) -> None:
        """Set multiple features to grouped_light at once."""
        # a grouped light can only handle OnFeature
        if (
            brightness is None
            and color_xy is None
            and color_temp is None
            and transition_time is None
        ):
            await self._send_put(id, GroupedLight(id, on=OnFeature(on=on)))
            return
        if transition_time is not None and transition_time < 100:
            raise AiohueException(
                "Transition needs to be specified in millisecond. Min 100, max 60000"
            )
        # redirect all other feature commands to underlying lights
        # note that this silently ignore params sent to light that are not supported
        await asyncio.gather(
            *[
                self._bridge.lights.set_state(
                    light.id,
                    on=on,
                    brightness=brightness if light.supports_dimming else None,
                    color_xy=color_xy if light.supports_color else None,
                    color_temp=color_temp if light.supports_color_temperature else None,
                    transition_time=transition_time,
                )
                for light in self.get_lights(id)
            ]
        )


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

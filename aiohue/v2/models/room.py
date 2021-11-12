"""Model(s) for Room resource on HUE bridge."""
from dataclasses import dataclass
from enum import Enum


from typing import Optional, Set, Type

from .group import Group
from .resource import (
    NamedResourceMetadata,
    ResourceTypes,
)


class RoomArchetype(Enum):
    """Possible archetypes of a room."""

    LIVING_ROOM = "living_room"
    KITCHEN = "kitchen"
    DINING = "dining"
    BEDROOM = "bedroom"
    KIDS_BEDROOM = "kids_bedroom"
    BATHROOM = "bathroom"
    NURSERY = "nursery"
    RECREATION = "recreation"
    OFFICE = "office"
    GYM = "gym"
    HALLWAY = "hallway"
    TOILET = "toilet"
    FRONT_DOOR = "front_door"
    GARAGE = "garage"
    TERRACE = "terrace"
    GARDEN = "garden"
    DRIVEWAY = "driveway"
    CARPORT = "carport"
    HOME = "home"
    DOWNSTAIRS = "downstairs"
    UPSTAIRS = "upstairs"
    TOP_FLOOR = "top_floor"
    ATTIC = "attic"
    GUEST_ROOM = "guest_room"
    STAIRCASE = "staircase"
    LOUNGE = "lounge"
    MAN_CAVE = "man_cave"
    COMPUTER = "computer"
    STUDIO = "studio"
    MUSIC = "music"
    TV = "tv"
    READING = "reading"
    CLOSET = "closet"
    STORAGE = "storage"
    LAUNDRY_ROOM = "laundry_room"
    BALCONY = "balcony"
    PORCH = "porch"
    BARBECUE = "barbecue"
    POOL = "pool"
    OTHER = "other"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return RoomArchetype.OTHER


@dataclass
class RoomMetadata(NamedResourceMetadata):
    """
    Represent RoomMetadata object as used by the Hue api.

    Configuration object for a room.

    clip-api.schema.json#/definitions/RoomMetadataGet
    clip-api.schema.json#/definitions/RoomMetadataPost
    clip-api.schema.json#/definitions/RoomMetadataPut
    """

    archetype: Optional[RoomArchetype] = None  # required in post/get, optional in put


@dataclass
class Room(Group):
    """
    Represent Room object as used by the Hue api.

    Room resources groups all devices within the same physical space of a room.
    Room only allows resources of type "device" as childs.
    A device can only be in at most one room.

    clip-api.schema.json#/definitions/RoomGet
    clip-api.schema.json#/definitions/RoomPost
    clip-api.schema.json#/definitions/RoomPut
    """

    metadata: Optional[RoomMetadata] = None  # required in post/get, optional in put
    type: ResourceTypes = ResourceTypes.ROOM

    @property
    def devices(self) -> Set[str]:
        """Return set of device id's that belong to this room."""
        return {x.rid for x in self.services}

    @property
    def grouped_light(self) -> Optional[str]:
        """Return the grouped light id that is connected to this room (if any)."""
        if not self.grouped_services:
            return None
        return next(
            (
                x.rid
                for x in self.grouped_services
                if x.rtype == ResourceTypes.GROUPED_LIGHT
            ),
            None,
        )

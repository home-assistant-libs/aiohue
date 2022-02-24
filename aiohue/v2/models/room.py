"""
Model(s) for Room resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_room
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set, Type


from .resource import ResourceIdentifier, ResourceTypes


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
class RoomMetaData:
    """Represent MetaData for a room resource."""

    archetype: RoomArchetype
    name: str


@dataclass
class RoomMetaDataPut:
    """
    Represent Room MetaData properties on update/PUT.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device__id__put
    """

    archetype: Optional[RoomArchetype]
    name: Optional[str]


@dataclass
class Room:
    """
    Represent a (full) `Room` object as retrieved from the Hue api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_room_get
    """

    id: str
    # services: required(array of ResourceIdentifier)
    # References all services aggregating control and state of children in the group
    # This includes all services grouped in the group hierarchy given by child relation
    # This includes all services of a device grouped in the group hierarchy given by child relation
    # Aggregation is per service type, ie every service type which can be grouped has a
    # corresponding definition of grouped type
    # Supported types “light”
    services: List[ResourceIdentifier]
    metadata: RoomMetaData

    # children: required(array of ResourceIdentifier)
    # Devices to group by the Room Following children are allowed: device
    children: List[ResourceIdentifier]

    id_v1: Optional[str] = None
    type: ResourceTypes = ResourceTypes.ROOM

    @property
    def devices(self) -> Set[str]:
        """Return set of device id's that belong to this room."""
        return {x.rid for x in self.children}

    @property
    def grouped_light(self) -> Optional[str]:
        """Return the grouped light id that is connected to this room (if any)."""
        if not self.services:
            return None
        return next(
            (x.rid for x in self.services if x.rtype == ResourceTypes.GROUPED_LIGHT),
            None,
        )

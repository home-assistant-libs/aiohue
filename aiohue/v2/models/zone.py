"""
Model(s) for Zone resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zone
"""

from dataclasses import dataclass

from .resource import ResourceTypes
from .room import Room, RoomPost, RoomPut


@dataclass
class Zone(Room):
    """
    Represent a (full) `Zone` object as retrieved from the Hue api.

    Zones group services and each service can be part of multiple zones.
    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zone_get
    """

    type: ResourceTypes = ResourceTypes.ZONE


@dataclass
class ZonePut(RoomPut):
    """
    Properties to send when updating/setting a `Zone` object on the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zone__id__put
    """


@dataclass
class ZonePost(RoomPost):
    """
    Properties to send when creating a `Zone` object on the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zone_post
    """

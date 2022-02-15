"""
Model(s) for Zone resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zone
"""
from dataclasses import dataclass
from typing import List, Optional, Set

from .resource import ResourceIdentifier, ResourceTypes
from .room import RoomMetaData


@dataclass
class Zone:
    """
    Represent a (full) `Zone` object as retrieved from the Hue api.

    Zones group services and each service can be part of multiple zones.
    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zone_get
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
    # Devices to group by the Room Following children are allowed: light
    children: List[ResourceIdentifier]

    id_v1: Optional[str] = None
    grouped_services: Optional[List[ResourceIdentifier]] = None
    type: ResourceTypes = ResourceTypes.ZONE

    @property
    def grouped_light(self) -> Optional[str]:
        """Return the grouped light id that is connected to this zone (if any)."""
        return next(
            (x.rid for x in self.services if x.rtype == ResourceTypes.GROUPED_LIGHT),
            None,
        )

    @property
    def lights(self) -> Set[str]:
        """Return a set of light id's belonging to this zone."""
        return {x.rid for x in self.children}

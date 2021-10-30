"""Generic Group/Service Models used by various Hue resources."""

from dataclasses import dataclass
from typing import List, Optional, Set

from .resource import SENSOR_RESOURCE_TYPES, Resource, ResourceIdentifier, ResourceTypes


@dataclass
class Group(Resource):
    """
    Supertype of all groups grouping devices or services.

    clip-api.schema.json#/definitions/Group
    """

    children: Optional[
        List[ResourceIdentifier]
    ] = None  # only available in get response
    services: Optional[
        List[ResourceIdentifier]
    ] = None  # only available in get response
    # grouped_services references all services aggregating control and
    # state of services in the group. This includes all services grouped
    # in the group hierarchy given by child relation. This includes all services
    # of a device grouped in the group hierarchy given by child relation.
    # Aggregation is per service type, ie every service type which can be grouped
    # has a corresponding definition of grouped type.
    # Supported types: 'light'
    grouped_services: Optional[List[ResourceIdentifier]] = None

    @property
    def lights(self) -> Set[str]:
        """Return a set of light id's belonging to this group/device."""
        if not self.services:
            return set()
        return {x.rid for x in self.services if x.rtype == ResourceTypes.LIGHT}

    @property
    def sensors(self) -> Set[str]:
        """Return a set of sensor id's belonging to this group/device."""
        if not self.services:
            return set()
        return {x.rid for x in self.services if x.rtype in SENSOR_RESOURCE_TYPES}

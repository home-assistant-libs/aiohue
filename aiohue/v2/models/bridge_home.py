"""
Model(s) for bridge_home resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_bridge_home
"""

from dataclasses import dataclass

from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class BridgeHome:
    """
    Represent the (full) `BridgeHome` object as retrieved from the Hue api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_bridge_home_get
    """

    id: str
    # services: required(array of ResourceIdentifier)
    # References all services aggregating control and state of children in the group
    # This includes all services grouped in the group hierarchy given by child relation
    # This includes all services of a device grouped in the group hierarchy given by child relation
    # Aggregation is per service type, ie every service type which can be grouped has a
    # corresponding definition of grouped type
    # Supported types “light”
    services: list[ResourceIdentifier]
    children: list[ResourceIdentifier]

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.BRIDGE_HOME

"""Model(s) for bridge_home resource on HUE bridge."""
from dataclasses import dataclass

from .resource import ResourceTypes
from .group import Group


@dataclass
class BridgeHome(Group):
    """
    Represent BridgeHome object as retrieved from the api.

    Home resource lists all rooms in a home and all devices which are not assigned to a room.
    Home only contains resources of type "device" and "room"

    clip-api.schema.json#/definitions/BridgeHomeGet
    clip-api.schema.json#/definitions/BridgeHomePut
    """

    type: ResourceTypes = ResourceTypes.BRIDGE_HOME

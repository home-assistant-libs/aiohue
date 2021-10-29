"""Model(s) for zigbee_connectivity resource on HUE bridge."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .resource import Resource, ResourceIdentifier, ResourceTypes


class ConnectivityServiceStatus(Enum):
    """
    Enum with possible ConnectivityService statuses.

    defined in clip-api.schema.json#/definitions/ConnectivityService
    """

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTIVITY_ISSUE = "connectivity_issue"


@dataclass
class ConnectivityService(Resource):
    """
    Represent ConnectivityService object as received from the api.

    clip-api.schema.json#/definitions/ConnectivityService
    """

    status: Optional[ConnectivityServiceStatus] = None  # required in get

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.status, (type(None), ConnectivityServiceStatus)):
            self.status = ConnectivityServiceStatus(self.status)


@dataclass
class ZigbeeConnectivity(ConnectivityService):
    """
    Represent ZigbeeConnectivity object as received from the api.

    clip-api.schema.json#/definitions/ZigbeeConnectivity
    """

    mac_address: Optional[str] = None  # can not be set
    type: ResourceTypes = ResourceTypes.ZIGBEE_CONNECTIVITY

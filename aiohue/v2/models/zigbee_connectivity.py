"""
Model(s) for zigbee_connectivity resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zigbee_connectivity
"""

from dataclasses import dataclass
from enum import Enum

from .resource import ResourceIdentifier, ResourceTypes


class ConnectivityServiceStatus(Enum):
    """
    Enum with possible ConnectivityService statuses.

    Connected if device has been recently been available.
    When indicating connectivity issues the device is powered off or has network
    issues When indicating unidirectional incoming the device only talks to bridge
    pending_discovery when device is expected to be discovered (added to the
    network) soon
    """

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTIVITY_ISSUE = "connectivity_issue"
    UNIDIRECTIONAL_INCOMING = "unidirectional_incoming"
    PENDING_DISCOVERY = "pending_discovery"


@dataclass
class ZigbeeConnectivity:
    """
    Represent a (full) `ZigbeeConnectivity` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zigbee_connectivity_get
    """

    id: str
    owner: ResourceIdentifier
    status: ConnectivityServiceStatus
    mac_address: str
    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.ZIGBEE_CONNECTIVITY

"""
Model(s) for zigbee_connectivity resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zigbee_connectivity
"""

from dataclasses import dataclass
from enum import Enum

from .feature import ConfigurationStatus
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


class ZigbeeChannelValue(Enum):
    """Enum with possible zigbee channels."""

    CHANNEL_11 = "channel_11"
    CHANNEL_15 = "channel_15"
    CHANNEL_20 = "channel_20"
    CHANNEL_25 = "channel_25"
    NOT_CONFIGURED = "not_configured"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return ZigbeeChannelValue.UNKNOWN


@dataclass
class ZigbeeChannel:
    """
    Represent the zigbee channel of a ZigbeeConnectivity resource.

    If the channel was recently changed, `value` reflects the channel that is
    currently being changed to.
    """

    value: ZigbeeChannelValue = ZigbeeChannelValue.UNKNOWN
    status: ConfigurationStatus = ConfigurationStatus.UNKNOWN


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
    # channel and extended_pan_id are only reported by the bridge's own service
    channel: ZigbeeChannel | None = None
    extended_pan_id: str | None = None
    type: ResourceTypes = ResourceTypes.ZIGBEE_CONNECTIVITY

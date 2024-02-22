"""
Model(s) for entertainment_configuration resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_entertainment_configuration
"""

from dataclasses import dataclass
from enum import Enum

from .feature import Position
from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class Segment:
    """
    Represent a Segment object.

    Contains the segments configuration of the device for entertainment purposes.
    A device can be segmented in a single way.
    """

    length: int
    start: int


@dataclass
class SegmentReference:
    """
    Represent a SegmentReference object.

    From which entertainment_service, which segment is a member of this channel.
    """

    service: ResourceIdentifier
    index: int


@dataclass
class EntertainmentChannel:
    """
    Represent a EntertainmentChannel object as used by the Hue api.

    Holds position of the channel and list of members,
    which is an array of segments resource identifiers.
    """

    channel_id: int
    # xyz position of this channel. It is the average position of its members.
    position: Position
    members: list[SegmentReference]


class EntertainmentConfigurationType(Enum):
    """Enum with possible Entertainment Configuration Types."""

    SCREEN = "screen"  # Channels are organized around content from a screen
    MUSIC = "music"  # Channels are organized for music synchronization
    THREEDEESPACE = "3dspace"  # Channels are organized to provide 3d spatial effects
    OTHER = "other"  # General use case "
    MONITOR = "monitor"  # Channels are organized around content from monitors


class EntertainmentStatus(Enum):
    """Enum with possible Entertainment Statuses."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class StreamingProxyMode(Enum):
    """Enum with possible StreamingProxy Modes."""

    AUTO = "auto"
    MANUAL = "manual"


@dataclass
class StreamingProxy:
    """Represent a StreamingProxy object as used by the Hue api."""

    mode: StreamingProxyMode
    node: ResourceIdentifier


@dataclass
class ServiceLocation:
    """Represent a ServiceLocation object as used by the Hue api."""

    service: ResourceIdentifier
    positions: list[Position]
    position: Position | None = None


@dataclass
class EntertainmentLocations:
    """
    Represent a EntertainmentLocations object as used by the Hue api.

    The position of each entertainment service in the configuration.
    If the service has several segments, more than one x,y,z location may be needed
    """

    service_locations: list[ServiceLocation]


class EntertainmentConfigurationAction(Enum):
    """
    Enum with possible Entertainment Configuration Actions.

    as defined in:
    clip-api.schema.json#/definitions/EntertainmentConfigurationPut
    """

    START = "start"
    STOP = "stop"


@dataclass
class EntertainmentConfigurationMetaData:
    """Represent EntertainmentConfigurationMetaData for a device object as used by the Hue api."""

    name: str


@dataclass
class EntertainmentConfiguration:
    """
    Represent a (full) `EntertainmentConfiguration` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_entertainment_configuration_get
    """

    id: str
    metadata: EntertainmentConfigurationMetaData
    configuration_type: EntertainmentConfigurationType
    status: EntertainmentStatus
    stream_proxy: StreamingProxy
    channels: list[EntertainmentChannel]
    locations: EntertainmentLocations
    light_services: list[ResourceIdentifier] | None = None

    active_streamer: ResourceIdentifier | None = None
    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.ENTERTAINMENT_CONFIGURATION

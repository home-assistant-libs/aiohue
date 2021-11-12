"""Model(s) for entertainment resource on HUE bridge."""
from dataclasses import dataclass
from enum import Enum


from typing import List, Optional

from .feature import Position
from .resource import NamedResourceMetadata, Resource, ResourceIdentifier, ResourceTypes


@dataclass
class Segment:
    """
    Represent a Segment object as used by the Hue api.

    Contains the segments configuration of the device for entertainment purposes.
    A device can be segmented in a single way.

    clip-api.schema.json#/definitions/Segment
    """

    length: int
    start: int


@dataclass
class SegmentReference:
    """
    Represent a SegmentReference object as used by the Hue api.

    From which entertainment_service, which segment is a member of this channel.

    clip-api.schema.json#/definitions/SegmentReferenceGet
    """

    service: ResourceIdentifier
    index: int


@dataclass
class SegmentationProperties:
    """
    Represent a SegmentationProperties dict type.

    All properties regarding the segment capabilities of this device:
    the configuratibility, max_segments and all segment tables.
    clip-api.schema.json#/definitions/Segment
    """

    configurable: bool
    max_segments: int
    segments: List[Segment]


@dataclass
class EntertainmentChannelGet:
    """
    Represent a EntertainmentChannel object as used by the Hue api.

    Holds position of the channel and list of members, which is an array of segments resource identifiers.

    clip-api.schema.json#/definitions/EntertainmentChannelGet
    """

    # Bridge assigns a number (0...255) upon creation.
    # This is the number to be used by the HueStream API when addressing the channel
    channel_id: int
    # xyz position of this channel. It is the average position of its members.
    position: Position
    members: List[SegmentReference]


class EntertainmentConfigurationType(Enum):
    """
    Enum with possible Entertainment Configuration Types.

    as defined in:
    clip-api.schema.json#/definitions/EntertainmentConfiguration
    """

    SCREEN = "screen"  # Channels are organized around content from a screen
    MUSIC = "music"  # Channels are organized for music synchronization
    THREEDEESPACE = "3dspace"  # Channels are organized to provide 3d spacial effects
    OTHER = "other"  # General use case "


class EntertainmentStatus(Enum):
    """
    Enum with possible Entertainment Statuses.

    as defined in:
    clip-api.schema.json#/definitions/EntertainmentConfiguration
    """

    ACTIVE = "active"
    INACTIVE = "inactive"


class StreamingProxyMode(Enum):
    """
    Enum with possible StreamingProxy Modes.

    as defined in:
    clip-api.schema.json#/definitions/StreamingProxy
    """

    AUTO = "auto"
    MANUAL = "manual"


@dataclass
class StreamingProxy:
    """
    Represent a StreamingProxy object as used by the Hue api.

    Holds position of the channel and list of members, which is an array of segments resource identifiers.

    clip-api.schema.json#/definitions/StreamingProxyGet
    """

    mode: StreamingProxyMode
    node: ResourceIdentifier


@dataclass
class ServiceLocation:
    """
    Represent a ServiceLocation object as used by the Hue api.

    clip-api.schema.json#/definitions/ServiceLocationGet
    """

    service: ResourceIdentifier
    position: Position
    positions: Optional[List[Position]] = None


@dataclass
class EntertainmentLocations:
    """
    Represent a EntertainmentLocations object as used by the Hue api.

    The position of each entertainment service in the configuration.
    If the service has several segments, more than one x,y,z location may be needed

    clip-api.schema.json#/definitions/EntertainmentLocationsGet
    """

    service_locations: List[ServiceLocation]


class EntertainmentConfigurationAction(Enum):
    """
    Enum with possible Entertainment Configuration Actions.

    as defined in:
    clip-api.schema.json#/definitions/EntertainmentConfigurationPut
    """

    START = "start"
    STOP = "stop"


@dataclass
class EntertainmentConfiguration(Resource):
    """
    Entertainment Configuration as used by the Hue api.

    clip-api.schema.json#/definitions/EntertainmentConfigurationGet
    clip-api.schema.json#/definitions/EntertainmentConfigurationPut
    """

    # Friendly name of the entertainment configuration (max 32 chars)
    name: Optional[str] = None
    # Defines for which type of application this channel assignment was optimized
    configuration_type: Optional[EntertainmentConfigurationType] = None
    # Read only field reporting if the stream is active or not
    status: Optional[EntertainmentStatus] = None
    # who's streaming: Expected value is of a ResourceIdentifier of the type auth_v1
    active_streamer: Optional[ResourceIdentifier] = None
    # the proxy that is in use
    stream_proxy: Optional[StreamingProxy] = None
    # Holds the channels. Each channel groups segments of one or different light
    channels: Optional[List[EntertainmentChannelGet]] = None
    # Holds the lights connected to this entertainment setup
    light_services: Optional[List[ResourceIdentifier]] = None
    # Entertertainment services of the lights that are in the zone have locations
    locations: Optional[EntertainmentLocations] = None
    # action: only available on update/put
    # If status is "inactive" -> write start to start streaming.
    # Writing start when it's already active does not change the owership of the streaming.
    # If status is "active" -> write "stop" to end the current streaming.
    # In order to start streaming when other application is already streaming,
    # first write "stop" and then "start"
    action: Optional[EntertainmentConfigurationAction] = None
    metadata: Optional[NamedResourceMetadata] = None
    type: Optional[ResourceTypes] = ResourceTypes.ENTERTAINMENT


@dataclass
class Entertainment(Resource):
    """
    Represent Entertainment resource as used by the Hue api.

    clip-api.schema.json#/definitions/EntertainmentGet
    """

    renderer: Optional[bool] = None
    proxy: Optional[bool] = None
    segments: Optional[SegmentationProperties] = None
    type: ResourceTypes = ResourceTypes.ENTERTAINMENT

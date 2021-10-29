"""Model(s) for entertainment resource on HUE bridge."""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from .feature import Position
from .resource import Resource, ResourceIdentifier, ResourceTypes


@dataclass
class Segment:
    """
    Represent a Segment object as received from the api.

    Contains the segments configuration of the device for entertainment purposes.
    A device can be segmented in a single way.

    clip-api.schema.json#/definitions/Segment
    """

    length: int
    start: int


@dataclass
class SegmentReference:
    """
    Represent a SegmentReference object as received from the api.

    From which entertainment_service, which segment is a member of this channel.

    clip-api.schema.json#/definitions/SegmentReferenceGet
    """

    service: ResourceIdentifier
    index: int

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.service, ResourceIdentifier):
            self.service = ResourceIdentifier(**self.service)


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

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if self.segments and not isinstance(self.segments[0], Segment):
            self.segments = [Segment(**x) for x in self.segments]


@dataclass
class EntertainmentChannelGet:
    """
    Represent a EntertainmentChannel object as received from the api.

    Holds position of the channel and list of members, which is an array of segments resource identifiers.

    clip-api.schema.json#/definitions/EntertainmentChannelGet
    """

    # Bridge assigns a number (0...255) upon creation.
    # This is the number to be used by the HueStream API when addressing the channel
    channel_id: int
    # xyz position of this channel. It is the average position of its members.
    position: Position
    members: List[SegmentReference]

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if self.position is not None and not isinstance(self.position, Position):
            self.position = Position(**self.position)
        if self.members and not isinstance(self.members[0], SegmentReference):
            self.members = [SegmentReference(**x) for x in self.members]


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
    Represent a StreamingProxy object as received from the api.

    Holds position of the channel and list of members, which is an array of segments resource identifiers.

    clip-api.schema.json#/definitions/StreamingProxyGet
    """

    mode: StreamingProxyMode
    node: ResourceIdentifier

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.mode, StreamingProxyMode):
            self.mode = StreamingProxyMode(self.mode)
        if not isinstance(self.node, ResourceIdentifier):
            self.node = ResourceIdentifier(**self.node)


@dataclass
class ServiceLocation:
    """
    Represent a ServiceLocation object as received from the api.

    clip-api.schema.json#/definitions/ServiceLocationGet
    """

    service: ResourceIdentifier
    position: Position

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.position, Position):
            self.position = Position(self.position)
        if not isinstance(self.service, ResourceIdentifier):
            self.service = ResourceIdentifier(**self.service)


@dataclass
class EntertainmentLocations:
    """
    Represent a EntertainmentLocations object as received from the api.

    The position of each entertainment service in the configuration.
    If the service has several segments, more than one x,y,z location may be needed

    clip-api.schema.json#/definitions/EntertainmentLocationsGet
    """

    service_locations: List[ServiceLocation]

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if self.service_locations and not isinstance(
            self.service_locations[0], ServiceLocation
        ):
            self.service_locations = [
                ServiceLocation(**x) for x in self.service_locations
            ]


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
    Entertainment Configuration as received from the api.

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
    # Entertertainment services of the lights that are in the zone have locations
    locations: Optional[List[EntertainmentLocations]] = None
    # action: only available on update/put
    # If status is "inactive" -> write start to start streaming.
    # Writing start when it's already active does not change the owership of the streaming.
    # If status is "active" -> write "stop" to end the current streaming.
    # In order to start streaming when other application is already streaming,
    # first write "stop" and then "start"
    action: Optional[EntertainmentConfigurationAction] = None
    type: Optional[ResourceTypes] = ResourceTypes.ENTERTAINMENT

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(
            self.configuration_type, (type(None), EntertainmentConfigurationType)
        ):
            self.configuration_type = EntertainmentConfigurationType(
                self.configuration_type
            )
        if not isinstance(self.status, (type(None), EntertainmentStatus)):
            self.status = EntertainmentStatus(self.status)
        if not isinstance(self.active_streamer, (type(None), ResourceIdentifier)):
            self.active_streamer = ResourceIdentifier(**self.active_streamer)
        if not isinstance(self.stream_proxy, (type(None), StreamingProxy)):
            self.stream_proxy = StreamingProxy(**self.stream_proxy)
        if self.channels and not isinstance(self.channels[0], EntertainmentChannelGet):
            self.channels = [EntertainmentChannelGet(**x) for x in self.channels]
        if self.locations and not isinstance(self.locations[0], EntertainmentLocations):
            self.locations = [EntertainmentLocations(**x) for x in self.locations]
        if not isinstance(self.action, (type(None), EntertainmentConfigurationAction)):
            self.action = EntertainmentConfigurationAction(self.action)


@dataclass
class Entertainment(Resource):
    """
    Represent Entertainment resource as received from the api.

    clip-api.schema.json#/definitions/EntertainmentGet
    """

    renderer: Optional[bool] = None
    proxy: Optional[bool] = None
    segments: Optional[SegmentationProperties] = None
    type: ResourceTypes = ResourceTypes.ENTERTAINMENT

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.segments, (type(None), SegmentationProperties)):
            self.segments = SegmentationProperties(**self.segments)

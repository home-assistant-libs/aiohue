"""Generic schemas for CLIP messages.."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, List, Type, TypeVar

from aiohue.util import dataclass_from_dict, parse_utc_timestamp

from ..models.light_level import LightLevel
from ..models.temperature import Temperature
from .behavior_instance import BehaviorInstance
from .behavior_script import BehaviorScript
from .bridge import Bridge
from .bridge_home import BridgeHome
from .button import Button
from .connectivity import ConnectivityService, ZigbeeConnectivity
from .depender import DependerGet
from .device import Device
from .device_power import DevicePower
from .entertainment import Entertainment, EntertainmentConfiguration
from .geofence_client import GeofenceClient
from .grouped_light import GroupedLight
from .homekit import HomekitGet
from .light import Light
from .motion import Motion
from .resource import Resource, ResourceTypes
from .room import Room
from .scene import Scene
from .zone import Zone

import logging

LOGGER = logging.getLogger(__package__)

CLIP_RESOURCE_MAPPING = {
    # Maps HUE resource type to correct class
    ResourceTypes.BEHAVIOR_INSTANCE: BehaviorInstance,
    ResourceTypes.BEHAVIOR_SCRIPT: BehaviorScript,
    ResourceTypes.BRIDGE: Bridge,
    ResourceTypes.BRIDGE_HOME: BridgeHome,
    ResourceTypes.BUTTON: Button,
    ResourceTypes.DEPENDER: DependerGet,
    ResourceTypes.DEVICE: Device,
    ResourceTypes.DEVICE_POWER: DevicePower,
    ResourceTypes.DEVICE_DISCOVERY: Resource,  # TODO
    ResourceTypes.DEVICE_UPDATE: Resource,  # TODO
    ResourceTypes.ENTERTAINMENT: Entertainment,
    ResourceTypes.ENTERTAINMENT_CONFIGURATION: EntertainmentConfiguration,
    ResourceTypes.GEOFENCE: Resource,  # TODO
    ResourceTypes.GEOFENCE_CLIENT: GeofenceClient,
    ResourceTypes.GROUPED_LIGHT: GroupedLight,
    ResourceTypes.HOMEKIT: HomekitGet,
    ResourceTypes.IP_CONNECTIVITY: ConnectivityService,  # TODO
    ResourceTypes.LIGHT: Light,
    ResourceTypes.LIGHT_LEVEL: LightLevel,
    ResourceTypes.MOTION: Motion,
    ResourceTypes.PUBLIC_IMAGE: Resource,  # TODO
    ResourceTypes.RELATIVE_ROTARY: Resource,  # TODO
    ResourceTypes.REMOTE_ACCESS: Resource,  # TODO
    ResourceTypes.ROOM: Room,
    ResourceTypes.SCENE: Scene,
    ResourceTypes.SYSTEM_UPDATE: Resource,  # TODO
    ResourceTypes.TEMPERATURE: Temperature,  # TODO
    ResourceTypes.ZIGBEE_BRIDGE_CONNECTIVITY: Resource,  # TODO
    ResourceTypes.ZIGBEE_CONNECTIVITY: ZigbeeConnectivity,
    ResourceTypes.ZONE: Zone,
    ResourceTypes.UNKNOWN: Resource,  # TODO
}
CLASS_TO_RESOURCE_MAPPING = {value: key for key, value in CLIP_RESOURCE_MAPPING.items()}

CLIPResource = TypeVar(
    "CLIPResource", *(Type[x] for x in CLIP_RESOURCE_MAPPING.values())
)


class CLIPEventType(Enum):
    """Type of the CLIP Event."""

    RESOURCE_ADDED = "add"
    RESOURCE_UPDATED = "update"
    RESOURCE_DELETED = "delete"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return CLIPEventType.UNKNOWN


def parse_clip_resource(obj_in: dict, strict=False) -> CLIPResource:
    """Parse raw object dict to correct CLIP Resource Class."""
    resource_type = ResourceTypes(obj_in["type"])
    resource_cls = CLIP_RESOURCE_MAPPING[resource_type]
    return dataclass_from_dict(resource_cls, obj_in, strict=False)


@dataclass
class CLIPEvent:
    """CLIP Event message as emitted by the EventStream."""

    id: str  # UUID
    creationtime: datetime
    type: CLIPEventType
    # data contains a list with resource objects
    # in case of add or update this is a full or partial resource object
    # in case of delete this will include only the
    # ResourceIndentifier (type and id) of the deleted object
    data: List[Resource]

    @classmethod
    def from_dict(cls: "CLIPEvent", dict_in: dict):
        """Create instance from dict."""
        return CLIPEvent(
            id=dict_in["id"],
            creationtime=parse_utc_timestamp(dict_in["creationtime"]),
            type=CLIPEventType(dict_in["type"]),
            data=[parse_clip_resource(x) for x in dict_in["data"]],
        )


@dataclass
class Error:
    """
    Error object which is returned when at least one error occured on a API call.

    clip-api.schema.json#/definitions/Error
    """

    # a human-readable explanation specific to this occurrence of the problem.
    description: str


@dataclass
class ClipMessage:
    """
    Basic message body for all return messages on GET, data contains full expanded resource.

    clip-api.schema.json#/definitions/ClipMessage
    """

    errors: List[Error]
    data: Any


@dataclass
class ClipMessageBehaviorInstance(ClipMessage):
    """
    CLIP Response when requesting behavior_instance resource.

    path: GET /clip/v2/resource/behavior_instance

    clip-api.schema.json#/definitions/ClipMessageBehaviorInstance
    """

    data: List[BehaviorInstance]


@dataclass
class ClipMessageBehaviorScript(ClipMessage):
    """
    CLIP Response when requesting behavior_script resource.

    path: GET /clip/v2/resource/behavior_script

    clip-api.schema.json#/definitions/ClipMessageBehaviorScript
    """

    data: List[BehaviorScript]


@dataclass
class ClipMessageBridge(ClipMessage):
    """
    CLIP Response when requesting bridge resource.

    path: GET /clip/v2/resource/bridge

    clip-api.schema.json#/definitions/ClipMessageBridge
    """

    data: List[Bridge]


@dataclass
class ClipMessageBridgeHome(ClipMessage):
    """
    CLIP Response when requesting bridge_home resource.

    path: GET /clip/v2/resource/bridge_home

    clip-api.schema.json#/definitions/ClipMessageBridgeHome
    """

    data: List[BridgeHome]


@dataclass
class ClipMessageButton(ClipMessage):
    """
    CLIP Response when requesting button resource.

    path: GET /clip/v2/resource/button

    clip-api.schema.json#/definitions/ClipMessageButton
    """

    data: List[Button]


@dataclass
class ClipMessageDependerGet(ClipMessage):
    """
    CLIP Response when requesting depender resource.

    path: GET /clip/v2/resource/depender

    clip-api.schema.json#/definitions/ClipMessageDependerGet
    """

    data: List[DependerGet]


@dataclass
class ClipMessageDevice(ClipMessage):
    """
    CLIP Response when requesting device resource.

    path: GET /clip/v2/resource/device

    clip-api.schema.json#/definitions/ClipMessageDevice
    """

    data: List[Device]


@dataclass
class ClipMessageEntertainmentConfiguration(ClipMessage):
    """
    CLIP Response when requesting entertainment_configuration resource.

    path: GET /clip/v2/resource/entertainment_configuration

    clip-api.schema.json#/definitions/ClipMessageEntertainmentConfiguration
    """

    data: List[EntertainmentConfiguration]


@dataclass
class ClipMessageEntertainment(ClipMessage):
    """
    CLIP Response when requesting entertainment resource.

    path: GET /clip/v2/resource/entertainment

    clip-api.schema.json#/definitions/ClipMessageEntertainment
    """

    data: List[Entertainment]


@dataclass
class ClipMessageGeofenceClient(ClipMessage):
    """
    CLIP Response when requesting geofence_client resource.

    path: GET /clip/v2/resource/geofence_client

    clip-api.schema.json#/definitions/ClipMessageGeofenceClient
    """

    data: List[GeofenceClient]


@dataclass
class ClipMessageGroupedLight(ClipMessage):
    """
    CLIP Response when requesting grouped_light resource.

    path: GET /clip/v2/resource/grouped_light

    clip-api.schema.json#/definitions/ClipMessageGroupedLight
    """

    data: List[GroupedLight]


@dataclass
class ClipMessageLight(ClipMessage):
    """
    CLIP Response when requesting light resource.

    path: GET /clip/v2/resource/light

    clip-api.schema.json#/definitions/ClipMessageLight
    """

    data: List[Light]


@dataclass
class ClipMessageMotion(ClipMessage):
    """
    CLIP Response when requesting motion resource.

    path: GET /clip/v2/resource/motion

    clip-api.schema.json#/definitions/ClipMessageMotion
    """

    data: List[Motion]


@dataclass
class ClipMessageResource(ClipMessage):
    """
    CLIP Response when requesting resource endpoint.

    path: GET /clip/v2/resource

    data will be an array containing all available resources inherited from Resource

    clip-api.schema.json#/definitions/ClipMessageResource
    """

    data: List[Resource]


@dataclass
class ClipMessageRoom(ClipMessage):
    """
    CLIP Response when requesting room resource.

    path: GET /clip/v2/resource/room

    clip-api.schema.json#/definitions/ClipMessageRoom
    """

    data: List[Room]


@dataclass
class ClipMessageScene(ClipMessage):
    """
    CLIP Response when requesting scene resource.

    path: GET /clip/v2/resource/scene

    clip-api.schema.json#/definitions/ClipMessageScene
    """

    data: List[Scene]


@dataclass
class ClipMessageZigbeeConnectivity(ClipMessage):
    """
    CLIP Response when requesting zigbee_connectivity resource.

    path: GET /clip/v2/resource/zigbee_connectivity

    clip-api.schema.json#/definitions/ClipMessageZigbeeConnectivity
    """

    data: List[ZigbeeConnectivity]


@dataclass
class ClipMessageZone(ClipMessage):
    """
    CLIP Response when requesting zone resource.

    path: GET /clip/v2/resource/zone

    clip-api.schema.json#/definitions/ClipMessageZone
    """

    data: List[Zone]

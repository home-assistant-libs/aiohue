"""Generic/base Resource Model(s)."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type


class ResourceTypes(Enum):
    """
    Type of the supported resources.

    clip-api.schema.json#/definitions/ResourceTypes
    """

    DEVICE = "device"
    BRIDGE_HOME = "bridge_home"
    ROOM = "room"
    ZONE = "zone"
    LIGHT = "light"
    BUTTON = "button"
    RELATIVE_ROTARY = "relative_rotary"
    TEMPERATURE = "temperature"
    LIGHT_LEVEL = "light_level"
    MOTION = "motion"
    ENTERTAINMENT = "entertainment"
    GROUPED_LIGHT = "grouped_light"
    DEVICE_POWER = "device_power"
    DEVICE_UPDATE = "device_update"
    IP_CONNECTIVITY = "ip_connectivity"
    ZIGBEE_BRIDGE_CONNECTIVITY = "zigbee_bridge_connectivity"
    ZIGBEE_CONNECTIVITY = "zigbee_connectivity"
    REMOTE_ACCESS = "remote_access"
    BRIDGE = "bridge"
    DEVICE_DISCOVERY = "device_discovery"
    SYSTEM_UPDATE = "system_update"
    SCENE = "scene"
    ENTERTAINMENT_CONFIGURATION = "entertainment_configuration"
    PUBLIC_IMAGE = "public_image"
    AUTH_V1 = "auth_v1"
    BEHAVIOR_SCRIPT = "behavior_script"
    BEHAVIOR_INSTANCE = "behavior_instance"
    GEOFENCE = "geofence"
    GEOFENCE_CLIENT = "geofence_client"
    DEPENDER = "depender"
    HOMEKIT = "homekit"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return ResourceTypes.UNKNOWN


SENSOR_RESOURCE_TYPES = (
    ResourceTypes.DEVICE_POWER,
    ResourceTypes.BUTTON,
    ResourceTypes.GEOFENCE_CLIENT,
    ResourceTypes.LIGHT_LEVEL,
    ResourceTypes.MOTION,
    ResourceTypes.RELATIVE_ROTARY,
    ResourceTypes.TEMPERATURE,
    ResourceTypes.ZIGBEE_CONNECTIVITY,
)


@dataclass
class Resource:
    """
    Represent a Resource object as used by the Hue api.

    clip-api.schema.json#/definitions/ResourceGet
    clip-api.schema.json#/definitions/ResourcePost
    clip-api.schema.json#/definitions/ResourcePut
    """

    id: str  # UUID
    type: ResourceTypes
    id_v1: Optional[str] = None


@dataclass
class ResourceMetadata:
    """
    Represent a ResourceMetadata object as used by the Hue api.

    Additional metadata stored for a resource.
    This provides additional information to the user to indentify a resource
    or to describe the resources context

    clip-api.schema.json#/definitions/ResourceMetadataGet
    clip-api.schema.json#/definitions/ResourceMetadataPost
    clip-api.schema.json#/definitions/ResourceMetadataPut
    """

    # string representation of the archetype of the resource
    archetype: Optional[str] = None


@dataclass
class NamedResourceMetadata(ResourceMetadata):
    """
    Represent a NamedResourceMetadata object as used by the Hue api.

    Additional metadata including a user given name

    clip-api.schema.json#/definitions/NamedResourceMetadataGet
    clip-api.schema.json#/definitions/NamedResourceMetadataPost
    clip-api.schema.json#/definitions/NamedResourceMetadataPut
    """

    #  Human readable name of a resource
    name: Optional[str] = None


@dataclass
class ResourceIdentifier:
    """
    Represent a ResourceIdentifier object as used by the Hue api.

    clip-api.schema.json#/definitions/ResourceIdentifierGet
    clip-api.schema.json#/definitions/ResourceIdentifierPost
    clip-api.schema.json#/definitions/ResourceIdentifierPut
    clip-api.schema.json#/definitions/ResourceIdentifierDelete
    """

    rid: str  # UUID
    rtype: ResourceTypes


@dataclass
class SensingService(Resource):
    """
    Represent a SensingService object as used by the Hue api.

    clip-api.schema.json#/definitions/SensingServiceGet
    clip-api.schema.json#/definitions/SensingServicePut
    """

    # optionnal bool if sensor is enabled
    enabled: Optional[bool] = None

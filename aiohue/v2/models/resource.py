"""Generic/base Resource Model(s)."""

from dataclasses import dataclass
from enum import Enum


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
    ZGP_CONNECTIVITY = "zgp_connectivity"
    REMOTE_ACCESS = "remote_access"
    BRIDGE = "bridge"
    DEVICE_DISCOVERY = "device_discovery"
    SYSTEM_UPDATE = "system_update"
    SCENE = "scene"
    SMART_SCENE = "smart_scene"
    ENTERTAINMENT_CONFIGURATION = "entertainment_configuration"
    PUBLIC_IMAGE = "public_image"
    AUTH_V1 = "auth_v1"
    BEHAVIOR_SCRIPT = "behavior_script"
    BEHAVIOR_INSTANCE = "behavior_instance"
    GEOFENCE = "geofence"
    GEOFENCE_CLIENT = "geofence_client"
    DEPENDER = "depender"
    HOMEKIT = "homekit"
    MATTER = "matter"
    MATTER_FABRIC = "matter_fabric"
    CONTACT = "contact"
    TAMPER = "tamper"
    CAMERA_MOTION = "camera_motion"
    PRIVATE_GROUP = "private_group"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
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

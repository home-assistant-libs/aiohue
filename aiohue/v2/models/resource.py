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
    CONVENIENCE_AREA_MOTION = "convenience_area_motion"
    SECURITY_AREA_MOTION = "security_area_motion"
    MOTION_AREA_CONFIGURATION = "motion_area_configuration"
    SERVICE_GROUP = "service_group"
    PRIVATE_GROUP = "private_group"
    GROUPED_MOTION = "grouped_motion"
    GROUPED_LIGHT_LEVEL = "grouped_light_level"
    BELL_BUTTON = "bell_button"

    # --- served resource types verified against a live Bridge Pro (2026-07) ---
    # `clip` enumerates every resource type the bridge serves - useful for
    # capability discovery and for spotting API additions early.
    CLIP = "clip"
    # NOTE: supersedes DEVICE_UPDATE, which no bridge reports anymore.
    DEVICE_SOFTWARE_UPDATE = "device_software_update"
    GEOLOCATION = "geolocation"
    SPEAKER = "speaker"
    SWITCH_INPUT_CONFIGURATION = "switch_input_configuration"
    # NOTE: supersedes DEVICE_DISCOVERY, which no bridge reports anymore.
    ZIGBEE_DEVICE_DISCOVERY = "zigbee_device_discovery"
    WIFI_CONNECTIVITY = "wifi_connectivity"

    # --- reference-only types ---
    # These never appear as a served resource, but the bridge does emit them
    # inside ResourceIdentifier.rtype. They need no model, only a valid enum
    # member so references round-trip instead of degrading to UNKNOWN.
    MOTION_AREA_CANDIDATE = "motion_area_candidate"
    RECIPE = "recipe"
    TAURUS_7455 = "taurus_7455"

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
    ResourceTypes.CONVENIENCE_AREA_MOTION,
    ResourceTypes.SECURITY_AREA_MOTION,
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

"""
Model(s) for device resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device
"""

from dataclasses import dataclass
from enum import Enum

from .feature import IdentifyFeature
from .resource import SENSOR_RESOURCE_TYPES, ResourceIdentifier, ResourceTypes


class DeviceArchetypes(Enum):
    """Enum with all possible Device archetypes."""

    BRIDGE_V2 = "bridge_v2"
    UNKNOWN_ARCHETYPE = "unknown_archetype"
    CLASSIC_BULB = "classic_bulb"
    SULTAN_BULB = "sultan_bulb"
    FLOOD_BULB = "flood_bulb"
    SPOT_BULB = "spot_bulb"
    CANDLE_BULB = "candle_bulb"
    LUSTER_BULB = "luster_bulb"
    PENDANT_ROUND = "pendant_round"
    PENDANT_LONG = "pendant_long"
    CEILING_ROUND = "ceiling_round"
    CEILING_SQUARE = "ceiling_square"
    FLOOR_SHADE = "floor_shade"
    FLOOR_LANTERN = "floor_lantern"
    TABLE_SHADE = "table_shade"
    RECESSED_CEILING = "recessed_ceiling"
    RECESSED_FLOOR = "recessed_floor"
    SINGLE_SPOT = "single_spot"
    DOUBLE_SPOT = "double_spot"
    TABLE_WASH = "table_wash"
    WALL_LANTERN = "wall_lantern"
    WALL_SHADE = "wall_shade"
    FLEXIBLE_LAMP = "flexible_lamp"
    GROUND_SPOT = "ground_spot"
    WALL_SPOT = "wall_spot"
    PLUG = "plug"
    HUE_GO = "hue_go"
    HUE_LIGHTSTRIP = "hue_lightstrip"
    HUE_IRIS = "hue_iris"
    HUE_BLOOM = "hue_bloom"
    BOLLARD = "bollard"
    WALL_WASHER = "wall_washer"
    HUE_PLAY = "hue_play"
    VINTAGE_BULB = "vintage_bulb"
    CHRISTMAS_TREE = "christmas_tree"
    STRING_LIGHT = "string_light"
    HUE_CENTRIS = "hue_centris"
    HUE_LIGHTSTRIP_TV = "hue_lightstrip_tv"
    HUE_LIGHTSTRIP_PC = "hue_lightstrip_pc"
    HUE_TUBE = "hue_tube"
    HUE_SIGNE = "hue_signe"
    PENDANT_SPOT = "pendant_spot"
    CEILING_HORIZONTAL = "ceiling_horizontal"
    CEILING_TUBE = "ceiling_tube"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return DeviceArchetypes.UNKNOWN_ARCHETYPE


@dataclass
class DeviceProductData:
    """Represent a DeviceProductData object as used by the Hue api."""

    model_id: str
    manufacturer_name: str
    product_name: str
    product_archetype: DeviceArchetypes
    certified: bool
    software_version: str
    # Hardware type; identified by Manufacturer code and ImageType
    hardware_platform_type: str | None = None


@dataclass
class DeviceMetaData:
    """Represent MetaData for a device object as used by the Hue api."""

    archetype: DeviceArchetypes
    name: str


@dataclass
class DeviceMetaDataPut:
    """Represent MetaData for a device object on update/PUT."""

    archetype: DeviceArchetypes | None
    name: str | None


@dataclass
class Device:
    """
    Represent a (full) `Device` resource as retrieved from the Hue api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device_get
    """

    id: str
    # services: required(array of ResourceIdentifierGet)
    # References all services aggregating control and state of children in the group
    # This includes all services grouped in the group hierarchy given by child relation
    # This includes all services of a device grouped in the group hierarchy given by child relation
    # Aggregation is per service type, ie every service type which can be grouped has a
    # corresponding definition of grouped type
    # Supported types “light”
    services: list[ResourceIdentifier]
    product_data: DeviceProductData
    metadata: DeviceMetaData

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.DEVICE

    @property
    def lights(self) -> set[str]:
        """Return a set of light id's belonging to this group/device."""
        return {x.rid for x in self.services if x.rtype == ResourceTypes.LIGHT}

    @property
    def sensors(self) -> set[str]:
        """Return a set of sensor id's belonging to this group/device."""
        return {x.rid for x in self.services if x.rtype in SENSOR_RESOURCE_TYPES}


@dataclass
class DevicePut:
    """
    Device resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device__id__put
    """

    metadata: DeviceMetaDataPut | None = None
    identify: IdentifyFeature | None = None

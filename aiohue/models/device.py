"""Model(s) for device resource on HUE bridge."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type

from .group import Group
from .resource import NamedResourceMetadata, ResourceTypes


class DeviceArchetypes(Enum):
    """
    Enum with all possible Device archtypes.

    clip-api.schema.json#/definitions/DeviceArchetypes
    """

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
    HUE_CENTRIS = "hue_centris"
    HUE_LIGHTSTRIP_TV = "hue_lightstrip_tv"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return DeviceArchetypes.UNKNOWN_ARCHETYPE


@dataclass(kw_only=True)
class DeviceProductData:
    """
    Represent a DeviceProductData object as received from the api.

    clip-api.schema.json#/definitions/DeviceProductData
    """

    model_id: str
    manufacturer_name: str
    product_name: str
    product_archetype: DeviceArchetypes
    certified: bool
    software_version: str
    product_id: Optional[str]  # missing in output from bridge ?


@dataclass(kw_only=True)
class DeviceMetaData(NamedResourceMetadata):
    """
    Represent DeviceMetaData object as received from the api.

    clip-api.schema.json#/definitions/DeviceMetaData
    """

    archetype: Optional[DeviceArchetypes]


@dataclass(kw_only=True)
class Device(Group):
    """
    Represent a Device object as received from the api.

    clip-api.schema.json#/definitions/DeviceGet
    clip-api.schema.json#/definitions/DevicePut
    """

    product_data: Optional[DeviceProductData]
    metadata: Optional[DeviceMetaData]  # optional in put
    creation_time: Optional[str]
    type: ResourceTypes = ResourceTypes.DEVICE

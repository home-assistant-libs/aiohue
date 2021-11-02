"""Model(s) for Light resource on HUE bridge."""
from dataclasses import dataclass
from enum import Enum


from typing import Any, List, Optional, Type

from .feature import (
    AlertFeature,
    ColorFeature,
    ColorTemperatureFeature,
    DimmingFeature,
    DynamicsFeature,
    DynamicsFeatureStatus,
    OnFeature,
)
from .resource import (
    NamedResourceMetadata,
    Resource,
    ResourceTypes,
)


class LightArchetypes(Enum):
    """
    Enum with all possible LightArchetypes.

    clip-api.schema.json#/definitions/LightArchetypes
    """

    UNKNOWN = "unknown_archetype"
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
        return LightArchetypes.UNKNOWN


@dataclass
class LightMetaData(NamedResourceMetadata):
    """
    Represent LightMetaData object as used by the Hue api.

    clip-api.schema.json#/definitions/LightMetaDataGet
    clip-api.schema.json#/definitions/LightMetaDataPut
    """

    archetype: Optional[LightArchetypes]


class LightModeValues(Enum):
    """
    Enum with all possible LightModes.

    clip-api.schema.json#/definitions/LightModeValues
    """

    NORMAL = "normal"
    STREAMING = "streaming"


@dataclass
class Gradient:
    """
    Represent Gradient object as used by the Hue api.

    TODO: Retrieve api spec.
    """

    points: Optional[List[Any]] = None
    points_capable: Optional[int] = None


@dataclass
class Light(Resource):
    """
    Represent a Light object as retrieved from the api.

    clip-api.schema.json#/definitions/LightGet
    clip-api.schema.json#/definitions/LightPut
    """

    metadata: Optional[LightMetaData] = None
    on: Optional[OnFeature] = None
    mode: Optional[LightModeValues] = None
    alert: Optional[AlertFeature] = None
    dimming: Optional[DimmingFeature] = None
    color_temperature: Optional[ColorTemperatureFeature] = None
    color: Optional[ColorFeature] = None
    dynamics: Optional[DynamicsFeature] = None
    gradient: Optional[Gradient] = None
    type: ResourceTypes = ResourceTypes.LIGHT

    @property
    def supports_dimming(self) -> bool:
        """Return if this light supports brightness control."""
        return self.dimming is not None

    @property
    def supports_color(self) -> bool:
        """Return if this light supports color control."""
        return self.color is not None

    @property
    def supports_color_temperature(self) -> bool:
        """Return if this light supports color_temperature control."""
        return self.color_temperature is not None

    @property
    def name(self) -> Optional[str]:
        """Return name from metadata."""
        if self.metadata is not None:
            return self.metadata.name
        return None

    @property
    def is_on(self) -> bool:
        """Return bool if light is currently powered on."""
        if self.on is not None:
            return self.on.on
        return False

    @property
    def brightness(self) -> float:
        """Return current brightness of light."""
        if self.dimming is not None:
            return self.dimming.brightness
        return 100.0 if self.is_on else 0.0

    @property
    def is_dynamic(self) -> bool:
        """Return bool if light is currently dynamically changing colors from a scene."""
        if self.dynamics is not None:
            return self.dynamics.status == DynamicsFeatureStatus.DYNAMIC_PALETTE
        return False

    @property
    def entertainment_active(self) -> bool:
        """Return bool if this light is currently streaming in Entertainment mode."""
        return self.mode == LightModeValues.STREAMING

"""Feature Schemas used by various Hue resources."""

from dataclasses import dataclass, field
from enum import Enum


from typing import List, Optional, Type


@dataclass
class OnFeatureBasic:
    """
    Represent OnFeatureBasic object as used by the Hue api.

    clip-api.schema.json#/definitions/OnFeatureBasic
    """

    on: bool


@dataclass
class OnFeature(OnFeatureBasic):
    """
    Represent OnFeature object, inherited from OnFeatureBasic.

    clip-api.schema.json#/definitions/OnFeature
    """


@dataclass
class DimmingFeatureBasic:
    """
    Represent DimmingFeatureBasic object as used by the Hue api.

    clip-api.schema.json#/definitions/DimmingFeatureBasic
    """

    # Brightness percentage between 0 and 100.
    brightness: float


@dataclass
class DimmingFeature(DimmingFeatureBasic):
    """
    Represent DimmingFeature object, inherits from DimmingFeatureBasic.

    clip-api.schema.json#/definitions/DimmingFeature
    """


@dataclass
class Position:
    """
    Represent Position object as used by the Hue api.

    Each Coordinate value is a float between -1 and 1.
    clip-api.schema.json#/definitions/Position
    """

    x: float
    y: float
    z: float


class AlertEffectType(Enum):
    """Enum with possible alert effect values."""

    BREATHE = "breathe"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return AlertEffectType.UNKNOWN


@dataclass
class AlertFeature:
    """Represent AlertFeature object as used by the Hue api."""

    action: Optional[AlertEffectType] = None
    action_values: List[AlertEffectType] = field(default_factory=list)


@dataclass
class ColorPoint:
    """
    CIE XY gamut position.

    Each position value is a float between -1 and 1.
    clip-api.schema.json#/definitions/ColorPoint
    """

    x: float
    y: float


@dataclass
class ColorFeatureGamut:
    """
    Color gamut of color bulb.

    Some bulbs do not properly return the Gamut information. In this case this is not present.
    clip-api.schema.json#/definitions/ColorFeatureGamut
    """

    red: ColorPoint
    green: ColorPoint
    blue: ColorPoint


class GamutType(Enum):
    """Enum with possible Gamut types."""

    A = "A"
    B = "B"
    C = "C"
    MIXED = "mixed"
    OTHER = "other"


@dataclass
class ColorFeatureBasic:
    """
    Represent ColorFeatureBasic object as used by the Hue api.

    clip-api.schema.json#/definitions/ColorFeatureBasic
    """

    xy: ColorPoint


@dataclass
class ColorFeature(ColorFeatureBasic):
    """
    Represent ColorFeature object as used by the Hue api.

    inherited from ColorFeatureBasic
    clip-api.schema.json#/definitions/ColorFeature
    """

    gamut_type: Optional[GamutType] = None
    gamut: Optional[ColorFeatureGamut] = None


@dataclass
class MirekSchema:
    """Represent Mirek schema."""

    mirek_maximum: int = 153
    mirek_minimum: int = 500


@dataclass
class ColorTemperatureFeatureBasic:
    """
    Represent ColorTemperatureFeatureBasic object as used by the Hue api.

    clip-api.schema.json#/definitions/ColorTemperatureFeatureBasic
    """

    # Color temperature in mirek (153-500) or None when the light color is not in the ct spectrum.
    mirek: Optional[int] = None
    mirek_schema: Optional[MirekSchema] = None
    # mirek_valid will be false if light is currently not in the ct spectrum
    mirek_valid: Optional[bool] = False


@dataclass
class ColorTemperatureFeature(ColorTemperatureFeatureBasic):
    """
    Represent ColorTemperatureFeature object, inherited from ColorTemperatureFeatureBasic.

    clip-api.schema.json#/definitions/ColorTemperatureFeature
    """


class DynamicsFeatureStatus(Enum):
    """Enum with all possible dynamic statuses."""

    NONE = "none"
    DYNAMIC_PALETTE = "dynamic_palette"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return DynamicsFeatureStatus.UNKNOWN


@dataclass
class DynamicsFeature:
    """Represent DynamicsFeature object as used by the Hue api."""

    status: Optional[DynamicsFeatureStatus] = None
    status_values: Optional[List[DynamicsFeatureStatus]] = None
    # Duration of a light transition in ms. Accuracy is in 100ms steps.
    # minimal value 100, maximum 6000000
    duration: Optional[int] = None  # transitionspeed: only sent on update/set
    speed: Optional[float] = None  # speed for the dynamics
    speed_valid: Optional[bool] = None  # speed for the dynamics


class RecallAction(Enum):
    """Enum with available recall actions."""

    ACTIVE = "active"
    DYNAMIC_PALETTE = "dynamic_palette"


@dataclass
class RecallFeature:
    """
    Properties to send when updating/setting RecallFeature on the api.

    clip-api.schema.json#/definitions/RecallFeature
    """

    action: Optional[RecallAction] = None
    status: Optional[str] = None
    # Duration of transition in ms. Accuracy is in 100ms steps.
    # minimal value 100, maximum 6000000
    duration: Optional[int] = None
    dimming: Optional[DimmingFeatureBasic] = None


@dataclass
class PaletteColor:
    """Represents PaletteColor feature used for PaletteFeature."""

    color: Optional[ColorFeatureBasic] = None
    dimming: Optional[DimmingFeatureBasic] = None


@dataclass
class PaletteColorTemperature:
    """Represents PaletteColorTemperature feature used for PaletteFeature."""

    color_temperature: Optional[ColorTemperatureFeatureBasic] = None
    dimming: Optional[DimmingFeatureBasic] = None


@dataclass
class PaletteFeature:
    """Represents Palette feature used for dynamic scenes."""

    color: Optional[List[PaletteColor]] = None
    color_temperature: Optional[List[PaletteColorTemperature]] = None
    dimming: Optional[List[DimmingFeatureBasic]] = None

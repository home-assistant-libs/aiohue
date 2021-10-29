"""Feature Schemas used by various Hue resources."""

from dataclasses import dataclass, field
from enum import Enum
from types import NoneType
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

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if self.brightness < 0 or self.brightness > 100:
            raise ValueError("brightness value should be in range of 0..100")


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

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.action, (NoneType, AlertEffectType)):
            self.action = AlertEffectType(self.action)
        if self.action_values and not isinstance(
            self.action_values[0], AlertEffectType
        ):
            self.action_values = [AlertEffectType(x) for x in self.action_values]


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

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.red, ColorPoint):
            self.red = ColorPoint(**self.red)
        if not isinstance(self.green, ColorPoint):
            self.green = ColorPoint(**self.green)
        if not isinstance(self.blue, ColorPoint):
            self.blue = ColorPoint(**self.blue)


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

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.xy, ColorPoint):
            self.xy = ColorPoint(**self.xy)


@dataclass
class ColorFeature(ColorFeatureBasic):
    """
    Represent ColorFeature object as used by the Hue api.

    inherited from ColorFeatureBasic
    clip-api.schema.json#/definitions/ColorFeature
    """

    gamut_type: Optional[GamutType] = None
    gamut: Optional[ColorFeatureGamut] = None

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        super().__post_init__()
        if not isinstance(self.gamut_type, (NoneType, GamutType)):
            self.gamut_type = GamutType(self.gamut_type)
        if not isinstance(self.gamut, (NoneType, ColorFeatureGamut)):
            self.gamut = ColorFeatureGamut(**self.gamut)


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
    mirek_schema: Optional[MirekSchema] = MirekSchema()
    # mirek_valid will be false if light is currently not in the ct spectrum
    mirek_valid: Optional[bool] = False

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.mirek_schema, (NoneType, MirekSchema)):
            self.mirek_schema = MirekSchema(**self.mirek_schema)


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
    speed: Optional[int] = None  # speed for the dynamics
    speed_valid: Optional[bool] = None  # speed for the dynamics

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.status, (NoneType, DynamicsFeatureStatus)):
            self.status = DynamicsFeatureStatus(self.status)
        if self.status_values and not isinstance(
            self.status_values[0], DynamicsFeatureStatus
        ):
            self.status = [DynamicsFeatureStatus(x) for x in self.status_values]


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

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if self.action and self.status:
            raise ValueError("action and status can not be set at the same time.")
        if not isinstance(self.action, (NoneType, RecallAction)):
            self.action = RecallAction(self.action)
        if not isinstance(self.dimming, (NoneType, DimmingFeatureBasic)):
            self.dimming = DimmingFeatureBasic(**self.dimming)


@dataclass
class PaletteColor:
    """Represents PaletteColor feature used for PaletteFeature."""

    color: Optional[ColorFeatureBasic] = None
    dimming: Optional[DimmingFeatureBasic] = None

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.color, (NoneType, ColorFeatureBasic)):
            self.color = ColorFeatureBasic(**self.color)
        if not isinstance(self.dimming, (NoneType, DimmingFeatureBasic)):
            self.dimming = DimmingFeatureBasic(**self.dimming)


@dataclass
class PaletteColorTemperature:
    """Represents PaletteColorTemperature feature used for PaletteFeature."""

    color_temperature: Optional[ColorTemperatureFeatureBasic] = None
    dimming: Optional[DimmingFeatureBasic] = None

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(
            self.color_temperature, (NoneType, ColorTemperatureFeatureBasic)
        ):
            self.color_temperature = ColorTemperatureFeatureBasic(
                **self.color_temperature
            )
        if not isinstance(self.dimming, (NoneType, DimmingFeatureBasic)):
            self.dimming = DimmingFeatureBasic(**self.dimming)


@dataclass
class PaletteFeature:
    """Represents Palette feature used for dynamic scenes."""

    color: Optional[List[PaletteColor]] = None
    color_temperature: Optional[List[PaletteColorTemperature]] = None
    dimming: Optional[List[DimmingFeatureBasic]] = None

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if self.color and not isinstance(self.color[0], PaletteColor):
            self.color = [PaletteColor(**x) for x in self.color]
        if self.color_temperature and not isinstance(
            self.color_temperature[0], PaletteColorTemperature
        ):
            self.color_temperature = [
                PaletteColorTemperature(**x) for x in self.color_temperature
            ]
        if self.dimming and not isinstance(self.dimming[0], DimmingFeatureBasic):
            self.dimming = [DimmingFeatureBasic(**x) for x in self.dimming]

"""Feature Schemas used by various Hue resources."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Type


@dataclass(kw_only=True)
class OnFeatureBasic:
    """
    Represent OnFeatureBasic object as received from the api.

    clip-api.schema.json#/definitions/OnFeatureBasic
    """

    on: bool


@dataclass(kw_only=True)
class OnFeature(OnFeatureBasic):
    """
    Represent OnFeature object, inherited from OnFeatureBasic.

    clip-api.schema.json#/definitions/OnFeature
    """


@dataclass(kw_only=True)
class DimmingFeatureBasic:
    """
    Represent DimmingFeatureBasic object as received from the api.

    clip-api.schema.json#/definitions/DimmingFeatureBasic
    """

    # Brightness percentage between 0 and 100.
    brightness: float


@dataclass(kw_only=True)
class DimmingFeature(DimmingFeatureBasic):
    """
    Represent DimmingFeature object, inherits from DimmingFeatureBasic.

    clip-api.schema.json#/definitions/DimmingFeature
    """


@dataclass
class Position:
    """
    Represent Position object as received from the api.

    Each Coordinate value is a float between -1 and 1.
    clip-api.schema.json#/definitions/Position
    """

    x: float
    y: float
    z: float


class AlertFeatureAction(Enum):
    """Enum with possible alert action values."""

    BREATHE = "breathe"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return AlertFeatureAction.UNKNOWN


@dataclass(kw_only=True)
class AlertFeature:
    """Represent AlertFeature object as received from the api."""

    action: Optional[AlertFeatureAction]
    action_values: List[AlertFeatureAction] = field(default_factory=list)


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


@dataclass(kw_only=True)
class ColorFeatureBasic:
    """
    Represent ColorFeatureBasic object as received from the api.

    clip-api.schema.json#/definitions/ColorFeatureBasic
    """

    xy: ColorPoint


@dataclass(kw_only=True)
class ColorFeature(ColorFeatureBasic):
    """
    Represent ColorFeature object as received from the api.

    inherited from ColorFeatureBasic
    clip-api.schema.json#/definitions/ColorFeature
    """

    gamut_type: Optional[GamutType]
    gamut: Optional[ColorFeatureGamut]


@dataclass
class MirekSchema:
    """Represent Mirek schema."""

    mirek_maximum: int = 153
    mirek_minimum: int = 500


@dataclass(kw_only=True)
class ColorTemperatureFeatureBasic:
    """
    Represent ColorTemperatureFeatureBasic object as received from the api.

    clip-api.schema.json#/definitions/ColorTemperatureFeatureBasic
    """

    # Color temperature in mirek (153-500) or None when the light color is not in the ct spectrum.
    mirek: Optional[int] = None
    mirek_schema: Optional[MirekSchema] = MirekSchema()
    # mirek_valid will be false if light is currently not in the ct spectrum
    mirek_valid: Optional[bool] = False


@dataclass(kw_only=True)
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


@dataclass(kw_only=True)
class DynamicsFeature:
    """Represent DynamicsFeature object as received from the api."""

    status: DynamicsFeatureStatus = DynamicsFeatureStatus.NONE
    status_values: List[DynamicsFeatureStatus] = field(default_factory=list)
    # Duration of a light transition in ms. Accuracy is in 100ms steps.
    # minimal value 100, maximum 6000000
    duration: Optional[int]  # only sent on update/set


class RecallAction(Enum):
    """Enum with available recall actions."""

    ACTIVE = "active"
    DYNAMIC_PALETTE = "dynamic_palette"


@dataclass(kw_only=True)
class RecallFeature:
    """
    Properties to send when updating/setting RecallFeature on the api.

    clip-api.schema.json#/definitions/RecallFeature
    """

    action: Optional[RecallAction]
    status: Optional[str]
    # Duration of transition in ms. Accuracy is in 100ms steps.
    # minimal value 100, maximum 6000000
    duration: Optional[int]
    dimming: Optional[DimmingFeatureBasic]

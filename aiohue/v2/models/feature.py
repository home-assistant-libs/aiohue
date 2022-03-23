"""Feature Schemas used by various Hue resources."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Type


@dataclass
class OnFeature:
    """Represent `On` Feature object as used by various Hue resources."""

    on: bool


@dataclass
class DimmingFeatureBase:
    """
    Represent `Dimming` Feature base properties.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    # brightness: (number - maximum: 100)
    # Brightness percentage. value cannot be 0, writing 0 changes it to lowest possible brightness
    brightness: float


@dataclass
class DimmingFeature(DimmingFeatureBase):
    """Represent `Dimming` Feature object as used by various Hue resources."""

    # Percentage of the maximum lumen the device outputs on minimum brightness
    min_dim_level: Optional[float] = None


@dataclass
class DimmingFeaturePut(DimmingFeatureBase):
    """Represent `Dimming` Feature when updating/sending in PUT requests."""


class DeltaAction(Enum):
    """Enum with delta actions for DimmingDelta and ColorDelta feature."""

    UP = "up"
    DOWN = "down"
    STOP = "stop"


@dataclass
class DimmingDeltaFeaturePut:
    """
    Represent `DimmingDelta` Feature when updating/sending in PUT requests.

    Brightness percentage of full-scale increase delta to current dimlevel. Clip at Max-level or Min-level.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    action: DeltaAction
    brightness_delta: Optional[float] = None


@dataclass
class ColorTemperatureDeltaFeaturePut:
    """
    Represent `DimmingDelta` Feature when updating/sending in PUT requests.

    Mirek delta to current mirek. Clip at mirek_minimum and mirek_maximum of mirek_schema.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    action: DeltaAction
    mirek_delta: Optional[int] = None


@dataclass
class Position:
    """
    Represent Position object as used by the Hue api.

    Each Coordinate value is a float between -1 and 1.
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
    """Represent AlertFeature object when retrieved from the Hue API."""

    action_values: List[AlertEffectType]


@dataclass
class AlertFeaturePut:
    """Represent AlertFeature object when sent to the Hue API."""

    action: AlertEffectType


@dataclass
class IdentifyFeature:
    """Represent IdentifyFeature object as used by the Hue api."""

    # only used in PUT requests on device
    action: str = "identify"


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
class ColorGamut:
    """
    Color gamut of color bulb.

    Some bulbs do not properly return the Gamut information. In this case this is not present.
    clip-api.schema.json#/definitions/ColorGamut
    """

    red: ColorPoint
    green: ColorPoint
    blue: ColorPoint


class GamutType(Enum):
    """
    Enum with possible Gamut types.

    The gammut types supported by hue.
        A: Gamut of early Philips color-only products.
        B: Limited gamut of first Hue color products.
        C: Richer color gamut of Hue white and color ambiance products.
        Other: Color gamut of non-hue products with non-hue gamuts resp w/o gamut.
    """

    A = "A"
    B = "B"
    C = "C"
    OTHER = "other"


@dataclass
class ColorFeatureBase:
    """Represent `Color` Feature base/required properties."""

    xy: ColorPoint


@dataclass
class ColorFeature(ColorFeatureBase):
    """Represent `Color` Feature object as used by various Hue resources."""

    gamut_type: GamutType = GamutType.OTHER
    gamut: Optional[ColorGamut] = None


@dataclass
class ColorFeaturePut(ColorFeatureBase):
    """Represent `Color` Feature when updating/sending in PUT requests."""


@dataclass
class MirekSchema:
    """Represent Mirek schema."""

    mirek_minimum: int = 153
    mirek_maximum: int = 500

    def __post_init__(self):
        """Auto correct invalid values."""
        # Fix for devices that provide wrong info
        if self.mirek_minimum == 0:
            self.mirek_minimum = 153
        if self.mirek_maximum == 65535:
            self.mirek_maximum = 500


@dataclass
class ColorTemperatureFeatureBase:
    """Represent `ColorTemperature` Feature base/required properties."""

    # Color temperature in mirek (153-500) or None if light not in CT spectrum
    mirek: Optional[int]


@dataclass
class ColorTemperatureFeature(ColorTemperatureFeatureBase):
    """Represent `ColorTemperature` Feature object as used by various Hue resources."""

    mirek_schema: MirekSchema
    # mirek_valid will be false if light is currently not in the ct spectrum
    mirek_valid: bool


@dataclass
class ColorTemperatureFeaturePut:
    """Represent `ColorTemperature` Feature when updating/sending in PUT requests."""

    # Color temperature in mirek (153-500)
    mirek: int


class DynamicStatus(Enum):
    """Enum with all possible dynamic statuses."""

    NONE = "none"
    DYNAMIC_PALETTE = "dynamic_palette"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return DynamicStatus.UNKNOWN


@dataclass
class DynamicsFeature:
    """
    Represent `DynamicsFeature` object as used by various Hue resources.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    # speed: required(number – minimum: 0 – maximum: 1)
    # speed of dynamic palette or effect. The speed is valid for the dynamic palette
    # if the status is dynamic_palette  or for the corresponding effect listed in status.
    # In case of status none, the speed is not valid
    speed: float
    # speed_valid: required(boolean)
    # Indicates whether the value presented in speed is valid
    speed_valid: bool
    # status: required(one of dynamic_palette, none)
    # Current status of the lamp with dynamics.
    status: DynamicStatus
    # status_values: required(array of SupportedDynamicStatus)
    # Statuses in which a lamp could be when playing dynamics.
    status_values: List[DynamicStatus] = field(default_factory=list)


@dataclass
class DynamicsFeaturePut:
    """
    Represent `DynamicsFeature` object when sent to the API in PUT requests.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    # speed: (number – minimum: 0 – maximum: 1)
    # speed of dynamic palette. The speed is valid for the dynamic palette if the status
    # is dynamic_palette or for the corresponding effect listed in status.
    # In case of status none, the speed is not valid
    speed: Optional[float] = None
    # duration: (integer – maximum: 6000000)
    # Duration of a light transition in ms. Accuracy is in 100ms steps.
    duration: Optional[int] = None


class EffectStatus(Enum):
    """Enum with possible effects."""

    NO_EFFECT = "no_effect"
    CANDLE = "candle"
    FIRE = "fire"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return EffectStatus.UNKNOWN


@dataclass
class EffectsFeature:
    """
    Represent `EffectsFeature` object as used by various Hue resources.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    status: EffectStatus
    status_values: List[EffectStatus] = field(default_factory=list)


@dataclass
class EffectsFeaturePut:
    """
    Represent `EffectsFeature` object when sent to the API in PUT requests.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    effect: EffectStatus


class TimedEffectStatus(Enum):
    """Enum with possible timed effects."""

    NO_EFFECT = "no_effect"
    SUNRISE = "sunrise"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return TimedEffectStatus.UNKNOWN


@dataclass
class TimedEffectsFeature:
    """
    Represent `TimedEffectsFeature` object as used by various Hue resources.

    Basic feature containing timed effect properties.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    status: EffectStatus
    status_values: List[EffectStatus] = field(default_factory=list)
    # Duration is mandatory when timed effect is set except for no_effect.
    # Resolution decreases for a larger duration. e.g Effects with duration smaller
    # than a minute will be rounded to a resolution of 1s, while effects with duration
    # larger than an hour will be arounded up to a resolution of 300s.
    # Duration has a max of 21600000 ms.
    duration: Optional[int] = None


@dataclass
class TimedEffectsFeaturePut:
    """
    Represent `TimedEffectsFeature` object when sent to the API in PUT requests.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    effect: Optional[TimedEffectStatus]
    # Duration is mandatory when timed effect is set except for no_effect.
    # Resolution decreases for a larger duration. e.g Effects with duration smaller
    # than a minute will be rounded to a resolution of 1s, while effects with duration
    # larger than an hour will be arounded up to a resolution of 300s.
    # Duration has a max of 21600000 ms.
    duration: Optional[int] = None


class RecallAction(Enum):
    """Enum with available recall actions."""

    ACTIVE = "active"
    DYNAMIC_PALETTE = "dynamic_palette"


@dataclass
class RecallFeature:
    """
    Properties to send when calling/setting the `Recall` feature (of a scene) on the api.

    clip-api.schema.json#/definitions/RecallFeature
    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_scene__id__put
    """

    # action: (RecallAction)
    # When writing active, the actions in the scene are executed on the target.
    action: Optional[RecallAction] = None
    # status: (active)
    # When writing active, the actions are executed on the target (legacy, use action insetad).
    status: Optional[str] = None
    # duration: (integer – maximum: 6000000)
    # transition to the scene within the timeframe given by duration. Accuracy is in 100ms steps.
    duration: Optional[int] = None
    # dimming: (DimmingFeature)
    # override the scene dimming/brightness
    dimming: Optional[DimmingFeature] = None


@dataclass
class PaletteFeatureColor:
    """Represents Color object used in PaletteFeature."""

    color: ColorFeatureBase
    dimming: DimmingFeatureBase


@dataclass
class PaletteFeatureColorTemperature:
    """Represents ColorTemperature object used in PaletteFeature."""

    color_temperature: ColorTemperatureFeatureBase
    dimming: DimmingFeatureBase


@dataclass
class PaletteFeature:
    """
    Group of colors that describe the palette of colors to be used when playing dynamics.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_scene__id__get
    """

    # color: required(array of PaletteFeatureColor – minItems: 0 – maxItems: 9)
    color: List[PaletteFeatureColor]
    # dimming: required(array of DimmingFeature – minItems: 0 – maxItems: 1)
    dimming: List[DimmingFeatureBase]
    # color_temperature: (array of PaletteFeatureColorTemperature – minItems: 0 – maxItems: 1)
    color_temperature: List[PaletteFeatureColorTemperature]


@dataclass
class GradientPoint:
    """Represent a single Gradient (color) Point."""

    color: ColorFeatureBase


@dataclass
class GradientFeatureBase:
    """Represent GradientFeature base properties."""

    # points: Collection of gradients points.
    # For control of the gradient points through a PUT a minimum of 2 points need to be provided.
    points: List[GradientPoint]


@dataclass
class GradientFeature(GradientFeatureBase):
    """
    Represent GradientFeature as used by the lights entities.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    # points_capable: required(integer)
    # Number of color points that gradient lamp is capable of showing with gradience.
    points_capable: int

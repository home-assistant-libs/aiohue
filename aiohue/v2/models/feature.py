"""Feature Schemas used by various Hue resources."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


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
    min_dim_level: float | None = None


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

    Brightness percentage of full-scale increase delta to current dimlevel.
    Clip at Max-level or Min-level.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    action: DeltaAction
    brightness_delta: float | None = None


@dataclass
class ColorTemperatureDeltaFeaturePut:
    """
    Represent `DimmingDelta` Feature when updating/sending in PUT requests.

    Mirek delta to current mirek. Clip at mirek_minimum and mirek_maximum of mirek_schema.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    action: DeltaAction
    mirek_delta: int | None = None


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
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return AlertEffectType.UNKNOWN


@dataclass
class AlertFeature:
    """Represent AlertFeature object when retrieved from the Hue API."""

    action_values: list[AlertEffectType]


@dataclass
class AlertFeaturePut:
    """Represent AlertFeature object when sent to the Hue API."""

    action: AlertEffectType


@dataclass
class IdentifyFeature:
    """
    Represent IdentifyFeature object as used by the Hue api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device__id__put
    identify: Triggers a visual identification sequence, current implemented as
    (which can change in the future):
    Bridge performs Zigbee LED identification cycles for 5 seconds Lights perform one breathe
    cycle Sensors perform LED identification cycles for 15 seconds
    """

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
    gamut: ColorGamut | None = None


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
    mirek: int | None


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
    def _missing_(cls: type, value: object):  # noqa: ARG003
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
    status_values: list[DynamicStatus] = field(default_factory=list)


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
    speed: float | None = None
    # duration: (integer – maximum: 6000000)
    # Duration of a light transition in ms. Accuracy is in 100ms steps.
    duration: int | None = None


class EffectStatus(Enum):
    """Enum with possible effects."""

    NO_EFFECT = "no_effect"
    CANDLE = "candle"
    FIRE = "fire"
    SPARKLE = "sparkle"
    GLISTEN = "glisten"
    OPAL = "opal"
    PRISM = "prism"
    UNDERWATER = "underwater"
    COSMOS = "cosmos"
    SUNBEAM = "sunbeam"
    ENCHANT = "enchant"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return EffectStatus.UNKNOWN


@dataclass
class SceneEffectsFeature:
    """
    Represent `EffectsFeature` base object as used by scenes.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_scene_get
    """

    effect: EffectStatus


@dataclass
class EffectsFeature:
    """
    Represent `EffectsFeature` object as used by various Hue resources.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    status: EffectStatus
    effect_values: list[EffectStatus] = field(default_factory=list)
    status_values: list[EffectStatus] = field(default_factory=list)


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
    SUNSET = "sunset"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return TimedEffectStatus.UNKNOWN


@dataclass
class TimedEffectsFeature:
    """
    Represent `TimedEffectsFeature` object as used by various Hue resources.

    Basic feature containing timed effect properties.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    status: TimedEffectStatus
    effect: TimedEffectStatus | None = None  # seems to be replaced by 'status'
    status_values: list[TimedEffectStatus] = field(default_factory=list)
    effect_values: list[TimedEffectStatus] = field(default_factory=list)
    # Duration is mandatory when timed effect is set except for no_effect.
    # Resolution decreases for a larger duration. e.g Effects with duration smaller
    # than a minute will be rounded to a resolution of 1s, while effects with duration
    # larger than an hour will be arounded up to a resolution of 300s.
    # Duration has a max of 21600000 ms.
    duration: int | None = None


@dataclass
class TimedEffectsFeaturePut:
    """
    Represent `TimedEffectsFeature` object when sent to the API in PUT requests.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    effect: TimedEffectStatus | None
    # Duration is mandatory when timed effect is set except for no_effect.
    # Resolution decreases for a larger duration. e.g Effects with duration smaller
    # than a minute will be rounded to a resolution of 1s, while effects with duration
    # larger than an hour will be arounded up to a resolution of 300s.
    # Duration has a max of 21600000 ms.
    duration: int | None = None


class RecallAction(Enum):
    """Enum with available recall actions."""

    ACTIVE = "active"
    STATIC = "static"
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
    action: RecallAction | None = None
    # status: (active, dynamic_palette)
    # When writing active, the actions are executed on the target (legacy, use action instead).
    status: str | None = None
    # duration: (integer – maximum: 6000000)
    # transition to the scene within the timeframe given by duration. Accuracy is in 100ms steps.
    duration: int | None = None
    # dimming: (DimmingFeature)
    # override the scene dimming/brightness
    dimming: DimmingFeatureBase | None = None


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
    color: list[PaletteFeatureColor]
    # dimming: required(array of DimmingFeature – minItems: 0 – maxItems: 1)
    dimming: list[DimmingFeatureBase]
    # color_temperature: (array of PaletteFeatureColorTemperature – minItems: 0 – maxItems: 1)
    color_temperature: list[PaletteFeatureColorTemperature]


@dataclass
class GradientPoint:
    """Represent a single Gradient (color) Point."""

    color: ColorFeatureBase


class GradientMode(Enum):
    """Mode of the Gradient feature."""

    INTERPOLATED_PALETTE = "interpolated_palette"
    INTERPOLATED_PALETTE_MIRRORED = "interpolated_palette_mirrored"
    RANDOM_PIXELATED = "random_pixelated"


@dataclass
class GradientFeatureBase:
    """Represent GradientFeature base properties."""

    # points: Collection of gradients points.
    # For control of the gradient points through a PUT a minimum of 2 points need to be provided.
    points: list[GradientPoint]


@dataclass
class GradientFeature(GradientFeatureBase):
    """
    Represent GradientFeature as used by the lights entities.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    # points_capable: required(integer)
    # Number of color points that gradient lamp is capable of showing with gradience.
    points_capable: int
    # mode: Mode in which the points are currently being deployed.
    # If not provided during PUT/POST it will be defaulted to interpolated_palette
    mode: GradientMode = GradientMode.INTERPOLATED_PALETTE
    mode_values: list[GradientMode] = field(default_factory=list)
    pixel_count: int | None = None  # Number of pixels in the device


class Signal(Enum):
    """Enum with various signals."""

    NO_SIGNAL = (
        "no_signal"  # No signal is active. Write “no_signal” to stop active signal.
    )
    ON_OFF = "on_off"  # Toggles between max brightness and Off in fixed color.
    ON_OFF_COLOR = (
        "on_off_color"  # Toggles between off and max brightness with color provided.
    )
    ALTERNATING = "alternating"  # Alternates between 2 provided colors.
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return Signal.UNKNOWN


@dataclass
class SignalingFeatureStatus:
    """Indicates status of active signal. Not available when inactive."""

    signal: Signal | None = Signal.UNKNOWN
    estimated_end: datetime | None = None
    colors: list[ColorFeatureBase] | None = None


@dataclass
class SignalingFeature:
    """Feature containing signaling properties."""

    # status: Indicates status of active signal. Not available when inactive.
    status: SignalingFeatureStatus | None = None
    # signal_values: Signals that the light supports.
    signal_values: list[Signal] = field(default_factory=list)


@dataclass
class SignalingFeaturePut:
    """Represent SignalingFeature object when sent to the Hue API."""

    signal: Signal
    # Duration has a max of 65534000 ms and a stepsize of 1 second.
    # Values in between steps will be rounded. Duration is ignored for no_signal.
    duration: int | None = None
    colors: list[ColorFeaturePut] | None = None


class PowerUpPreset(Enum):
    """Enum with available powerup presets."""

    SAFETY = "safety"
    POWERFAIL = "powerfail"
    LAST_ON_STATE = "last_on_state"
    CUSTOM = "custom"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return PowerUpPreset.UNKNOWN


class PowerUpFeatureOnMode(Enum):
    """Enum with available powerup on modes."""

    ON = "on"
    TOGGLE = "toggle"
    PREVIOUS = "previous"


@dataclass
class PowerUpFeatureOnState:
    """
    State to activate after powerup.

    On will use the value specified in the “on” property.
    When setting mode “on”, the on property must be included.
    Toggle will alternate between on and off on each subsequent power toggle.
    Previous will return to the state it was in before powering off.
    """

    mode: PowerUpFeatureOnMode
    on: OnFeature | None = None


class PowerUpFeatureDimmingMode(Enum):
    """Enum with available powerup dimming modes."""

    DIMMING = "dimming"
    PREVIOUS = "previous"


@dataclass
class PowerUpFeatureDimmingState:
    """
    Dimming will set the brightness to the specified value after power up.

    When setting mode “dimming”, the dimming property must be included.
    Previous will set brightness to the state it was in before powering off.
    """

    mode: PowerUpFeatureDimmingMode
    dimming: DimmingFeatureBase | None = None


class PowerUpFeatureColorMode(Enum):
    """Enum with available powerup color modes."""

    COLOR_TEMPERATURE = "color_temperature"
    COLOR = "color"
    PREVIOUS = "previous"


@dataclass
class PowerUpFeatureColorState:
    """
    Color state to activate after powerup.

    Availability of “color_temperature” and “color” modes depend on the capabilities of the lamp.
    Colortemperature will set the colortemperature to the specified value after power up.
    When setting color_temperature, the color_temperature property must be included Color will
    set the color tot he specified value after power up. When setting color mode,
    the color property must be included Previous will set color to the state
    it was in before powering off.
    """

    mode: PowerUpFeatureColorMode
    color_temperature: ColorTemperatureFeatureBase | None = None
    color: ColorFeatureBase | None = None


@dataclass
class PowerUpFeature:
    """
    Feature containing properties to configure powerup behaviour of a lightsource.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    # NOTE: When setting the custom preset the additional properties can be set.
    # For all other presets, no other properties can be included.
    preset: PowerUpPreset
    configured: bool
    on: PowerUpFeatureOnState
    dimming: PowerUpFeatureDimmingState | None = None
    color: PowerUpFeatureColorState | None = None


@dataclass
class PowerUpFeaturePut:
    """
    PowerUp feature properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    preset: PowerUpPreset
    on: PowerUpFeatureOnState | None = None
    dimming: PowerUpFeatureDimmingState | None = None
    color: PowerUpFeatureColorState | None = None


@dataclass
class MotionReport:
    """
    Represent MotionReport as retrieved from api.

    Used by `motion` and `camera_motion` resources.
    """

    changed: datetime
    motion: bool


@dataclass
class MotionSensingFeature:
    """
    Represent MotionSensingFeature object as retrieved from api.

    Used by `motion` and `camera_motion` resources.
    """

    motion_report: MotionReport | None = None
    motion: bool | None = None  # deprecated
    motion_valid: bool | None = None  # deprecated

    @property
    def value(self) -> bool | None:
        """Return the actual/current value."""
        # prefer new style attribute (not available on older firmware versions)
        if self.motion_report is not None:
            return self.motion_report.motion
        return self.motion


class MotionSensingFeatureSensitivityStatus(Enum):
    """Enum with possible Sensitivity statuses."""

    SET = "set"
    CHANGING = "changing"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return MotionSensingFeatureSensitivityStatus.UNKNOWN


@dataclass
class MotionSensingFeatureSensitivity:
    """
    Represent MotionSensingFeatureSensitivity as retrieved from api.

    Used by `motion` and `camera_motion` resources.
    """

    status: MotionSensingFeatureSensitivityStatus
    sensitivity: int
    sensitivity_max: int = 10


@dataclass
class MotionSensingFeatureSensitivityPut:
    """
    Represent MotionSensingFeatureSensitivity when set/updated with a PUT request.

    Used by `motion` and `camera_motion` resources.
    """

    sensitivity: int

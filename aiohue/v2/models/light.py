"""
Model(s) for Light resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light
"""

from dataclasses import dataclass
from enum import Enum

from .feature import (
    AlertFeature,
    AlertFeaturePut,
    ColorFeature,
    ColorFeatureBase,
    ColorTemperatureDeltaFeaturePut,
    ColorTemperatureFeature,
    ColorTemperatureFeatureBase,
    DimmingDeltaFeaturePut,
    DimmingFeature,
    DimmingFeatureBase,
    DynamicsFeature,
    DynamicsFeaturePut,
    DynamicStatus,
    EffectsFeature,
    EffectsFeaturePut,
    GradientFeature,
    GradientFeatureBase,
    OnFeature,
    PowerUpFeature,
    PowerUpFeaturePut,
    SignalingFeature,
    SignalingFeaturePut,
    TimedEffectsFeature,
    TimedEffectsFeaturePut,
)
from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class LightMetaData:
    """
    Represent LightMetaData object as used by the Hue api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    # Light archetype Deprecated: use archetype on device level
    archetype: str | None
    name: str


class LightMode(Enum):
    """
    Enum with all possible LightModes.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    NORMAL = "normal"
    STREAMING = "streaming"


@dataclass
class Light:
    """
    Represent a (full) `Light` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    # pylint: disable=too-many-instance-attributes

    id: str
    owner: ResourceIdentifier
    on: OnFeature
    mode: LightMode

    id_v1: str | None = None
    dimming: DimmingFeature | None = None
    color_temperature: ColorTemperatureFeature | None = None
    color: ColorFeature | None = None
    dynamics: DynamicsFeature | None = None
    alert: AlertFeature | None = None
    signaling: SignalingFeature | None = None
    gradient: GradientFeature | None = None
    effects: EffectsFeature | None = None
    timed_effects: TimedEffectsFeature | None = None
    powerup: PowerUpFeature | None = None

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
            return self.dynamics.status == DynamicStatus.DYNAMIC_PALETTE
        return False

    @property
    def entertainment_active(self) -> bool:
        """Return bool if this light is currently streaming in Entertainment mode."""
        return self.mode == LightMode.STREAMING


@dataclass
class LightPut:
    """
    Light resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    on: OnFeature | None = None
    dimming: DimmingFeatureBase | None = None
    dimming_delta: DimmingDeltaFeaturePut | None = None
    color_temperature: ColorTemperatureFeatureBase | None = None
    color_temperature_delta: ColorTemperatureDeltaFeaturePut | None = None
    color: ColorFeatureBase | None = None
    dynamics: DynamicsFeaturePut | None = None
    alert: AlertFeaturePut | None = None
    gradient: GradientFeatureBase | None = None
    effects: EffectsFeaturePut | None = None
    timed_effects: TimedEffectsFeaturePut | None = None
    powerup: PowerUpFeaturePut | None = None
    signaling: SignalingFeaturePut | None = None

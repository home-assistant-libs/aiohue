"""
Model(s) for Light resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

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
    archetype: Optional[str]
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

    id: str
    owner: ResourceIdentifier
    metadata: LightMetaData
    on: OnFeature
    mode: LightMode

    id_v1: Optional[str] = None
    dimming: Optional[DimmingFeature] = None
    color_temperature: Optional[ColorTemperatureFeature] = None
    color: Optional[ColorFeature] = None
    dynamics: Optional[DynamicsFeature] = None
    alert: Optional[AlertFeature] = None
    gradient: Optional[GradientFeature] = None
    effects: Optional[EffectsFeature] = None
    timed_effects: Optional[TimedEffectsFeature] = None

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

    on: Optional[OnFeature] = None
    dimming: Optional[DimmingFeatureBase] = None
    dimming_delta: Optional[DimmingDeltaFeaturePut] = None
    color_temperature: Optional[ColorTemperatureFeatureBase] = None
    color_temperature_delta: Optional[ColorTemperatureDeltaFeaturePut] = None
    color: Optional[ColorFeatureBase] = None
    dynamics: Optional[DynamicsFeaturePut] = None
    alert: Optional[AlertFeaturePut] = None
    gradient: Optional[GradientFeatureBase] = None
    effects: Optional[EffectsFeaturePut] = None
    timed_effects: Optional[TimedEffectsFeaturePut] = None

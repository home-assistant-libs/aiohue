"""
Model(s) for grouped_light resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_light
"""
from dataclasses import dataclass

from .feature import (
    AlertFeature,
    AlertFeaturePut,
    ColorFeaturePut,
    ColorTemperatureDeltaFeaturePut,
    ColorTemperatureFeaturePut,
    DimmingDeltaFeaturePut,
    DimmingFeatureBase,
    DynamicsFeaturePut,
    OnFeature,
)
from .resource import ResourceTypes


@dataclass
class GroupedLight:
    """
    Represent a (full) GroupedLight object when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_light_get
    """

    id: str
    id_v1: str | None = None
    on: OnFeature | None = None
    dimming: DimmingFeatureBase | None = None
    alert: AlertFeature | None = None
    type: ResourceTypes = ResourceTypes.GROUPED_LIGHT


@dataclass
class GroupedLightPut:
    """
    Represent a GroupedLight model when sending a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_light__id__put
    """

    on: OnFeature | None = None
    dimming: DimmingFeatureBase | None = None
    dimming_delta: DimmingDeltaFeaturePut | None = None
    color_temperature: ColorTemperatureFeaturePut | None = None
    color_temperature_delta: ColorTemperatureDeltaFeaturePut | None = None
    color: ColorFeaturePut | None = None
    dynamics: DynamicsFeaturePut | None = None
    alert: AlertFeaturePut | None = None

"""
Model(s) for grouped_light resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_light
"""
from dataclasses import dataclass
from typing import Optional

from .feature import AlertFeature, AlertFeaturePut, OnFeature
from .resource import ResourceTypes


@dataclass
class GroupedLight:
    """
    Represent a (full) GroupedLight object when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_light_get
    """

    id: str
    id_v1: Optional[str] = None
    on: Optional[OnFeature] = None
    alert: Optional[AlertFeature] = None
    type: ResourceTypes = ResourceTypes.GROUPED_LIGHT


@dataclass
class GroupedLightPut:
    """
    Represent a GroupedLight model when sending a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_light__id__put
    """

    on: Optional[OnFeature] = None
    alert: Optional[AlertFeaturePut] = None

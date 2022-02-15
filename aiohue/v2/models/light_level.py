"""
Model(s) for light_level resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_level
"""
from dataclasses import dataclass
from typing import Optional

from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class LightLevelFeature:
    """Represent LightLevel Feature used by Lightlevel resources."""

    light_level: int
    light_level_valid: bool


@dataclass
class LightLevel:
    """
    Represent a (full) `LightLevel` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_level_get
    """

    id: str
    owner: ResourceIdentifier
    enabled: bool
    light: LightLevelFeature

    id_v1: Optional[str] = None
    type: ResourceTypes = ResourceTypes.LIGHT_LEVEL


@dataclass
class LightLevelPut:
    """
    LightLevel resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_level__id__put
    """

    enabled: Optional[bool] = None

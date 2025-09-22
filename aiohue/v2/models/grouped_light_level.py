"""
Model(s) for grouped_light_level resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_light_level
"""

from dataclasses import dataclass

from aiohue.v2.models.light_level import LightLevelFeature

from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class GroupedLightLevel:
    """
    Represent a (full) `GroupedLightLevel` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_light_level_get
    """

    id: str
    owner: ResourceIdentifier
    enabled: bool
    light: LightLevelFeature

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.GROUPED_LIGHT_LEVEL


@dataclass
class GroupedLightLevelPut:
    """
    GroupedLightLevel resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_light_level__id__put
    """

    enabled: bool | None = None
    type: ResourceTypes = ResourceTypes.GROUPED_LIGHT_LEVEL

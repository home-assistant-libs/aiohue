"""
Model(s) for grouped_motion resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_motion
"""

from dataclasses import dataclass

from .feature import (
    MotionSensingFeature,
)
from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class GroupedMotion:
    """
    Represent a (full) `GroupedMotion` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_motion_get
    """

    id: str
    owner: ResourceIdentifier
    # enabled: required(boolean)
    # true when sensor is activated, false when deactivated
    enabled: bool
    motion: MotionSensingFeature

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.GROUPED_MOTION


@dataclass
class GroupedMotionPut:
    """
    GroupedMotion resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_grouped_motion__id__put
    """

    enabled: bool | None = None
    type: ResourceTypes = ResourceTypes.GROUPED_MOTION

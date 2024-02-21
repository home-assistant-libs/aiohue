"""
Model(s) for motion resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_motion
"""

from dataclasses import dataclass

from .feature import (
    MotionSensingFeature,
    MotionSensingFeatureSensitivity,
    MotionSensingFeatureSensitivityPut,
)
from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class Motion:
    """
    Represent a (full) `Motion` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_motion_get
    """

    id: str
    owner: ResourceIdentifier
    # enabled: required(boolean)
    # true when sensor is activated, false when deactivated
    enabled: bool
    motion: MotionSensingFeature
    sensitivity: MotionSensingFeatureSensitivity | None

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.MOTION


@dataclass
class MotionPut:
    """
    Motion resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_motion__id__put
    """

    enabled: bool | None = None
    sensitivity: MotionSensingFeatureSensitivityPut | None = None

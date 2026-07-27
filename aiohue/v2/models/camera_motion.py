"""
Model(s) for camera_motion resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_camera_motion
"""

from dataclasses import dataclass

from .feature import (
    MotionSensingFeature,
    MotionSensingFeatureSensitivity,
    MotionSensingFeatureSensitivityPut,
)
from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class CameraMotion:
    """
    Represent a (full) `CameraMotion` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_camera_motion_get
    """

    id: str
    owner: ResourceIdentifier
    # enabled: required(boolean)
    # true when sensor is activated, false when deactivated
    enabled: bool
    # NOTE: the bridge omits `motion` entirely on some firmware/config
    # combinations (notably Hue Secure / MotionAware areas). It must stay
    # optional or the whole resource fails to parse and gets dropped.
    motion: MotionSensingFeature | None = None
    sensitivity: MotionSensingFeatureSensitivity | None = None

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.CAMERA_MOTION


@dataclass
class CameraMotionPut:
    """
    CameraMotion resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_camera_motion__id__put
    """

    enabled: bool | None = None
    sensitivity: MotionSensingFeatureSensitivityPut | None = None

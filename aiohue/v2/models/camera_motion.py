"""
Model(s) for camera_motion resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_camera_motion
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Type

from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class CameraMotionReport:
    """
    Represent CameraMotionReport as retrieved from api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_camera_motion_get
    """

    changed: datetime
    motion: bool


@dataclass
class CameraMotionMotion:
    """
    Represent CameraMotionMotion object as retrieved from api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_camera_motion_get
    """

    motion_report: CameraMotionReport
    motion: Optional[bool] = None  # deprecated
    motion_valid: Optional[bool] = None  # deprecated


class CameraMotionSensitivityStatus(Enum):
    """Status of CameraMotionSensitivity."""

    SET = "set"
    CHANGING = "changing"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: object):
        """Set default enum member if an unknown value is provided."""
        return ResourceTypes.UNKNOWN


@dataclass
class CameraMotionSensitivity:
    """
    Represent CameraMotionSensitivity as retrieved from api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_camera_motion_get
    """

    status: CameraMotionSensitivityStatus
    sensitivity: int
    sensitivity_max: int = 10


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
    motion: CameraMotionMotion
    sensitivity: Optional[CameraMotionSensitivity]

    id_v1: Optional[str] = None
    type: ResourceTypes = ResourceTypes.CAMERA_MOTION


@dataclass
class CameraMotionSensitivityPut:
    """
    Represent CameraMotionSensitivity when set/updated with a PUT rquest.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_camera_motion__id__put
    """

    sensitivity: int


@dataclass
class CameraMotionPut:
    """
    CameraMotion resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_camera_motion__id__put
    """

    enabled: Optional[bool] = None
    sensitivity: Optional[CameraMotionSensitivityPut] = None

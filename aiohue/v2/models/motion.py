"""Model(s) for motion resource on HUE bridge."""
from dataclasses import dataclass


from typing import Optional

from .resource import SensingService, ResourceTypes


@dataclass
class MotionSensingFeature:
    """
    Represent MotionSensingFeature as retrieved from api.

    clip-api.schema.json#/definitions/MotionSensingFeatureGet
    """

    motion: Optional[bool] = None
    motion_valid: Optional[bool] = None


@dataclass
class Motion(SensingService):
    """
    Represent a Motion resource, a service detecting motion.

    clip-api.schema.json#/definitions/Motion
    """

    motion: Optional[MotionSensingFeature] = None
    type: ResourceTypes = ResourceTypes.MOTION

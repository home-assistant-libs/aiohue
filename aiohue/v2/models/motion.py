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

    motion: bool
    motion_valid: Optional[bool] = None


@dataclass
class Motion(SensingService):
    """
    Represent a Motion resource, a service detecting motion.

    clip-api.schema.json#/definitions/Motion
    """

    motion: Optional[MotionSensingFeature] = None
    type: ResourceTypes = ResourceTypes.MOTION

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        super().__post_init__()
        if not isinstance(self.motion, (type(None), MotionSensingFeature)):
            self.motion = MotionSensingFeature(**self.motion)

"""Model(s) for motion resource on HUE bridge."""
from dataclasses import dataclass
from typing import Optional

from .resource import Resource, ResourceTypes


@dataclass
class SensingService(Resource):
    """
    Represent a SensingService object as received from the api.

    clip-api.schema.json#/definitions/SensingServiceGet
    clip-api.schema.json#/definitions/SensingServicePut
    """


@dataclass
class MotionSensingFeature:
    """
    Represent MotionSensingFeature as retrieved from api.

    clip-api.schema.json#/definitions/MotionSensingFeatureGet
    """

    motion: bool


@dataclass
class Motion(SensingService):
    """
    Represent a Motion resource, a service detecting motion.

    clip-api.schema.json#/definitions/Motion
    """

    motion: Optional[MotionSensingFeature] = None
    type: ResourceTypes = ResourceTypes.MOTION

"""Model(s) for light_level resource on HUE bridge."""
from dataclasses import dataclass
from typing import Optional

from .resource import Resource, ResourceTypes


@dataclass
class LightLevelFeature:
    """Represent LightLevelFeature."""

    light_level: Optional[int] = None
    light_level_valid: bool = True


@dataclass
class LightLevel(Resource):
    """
    Represent a LightLevel resource, a sensor reporting Illuminance in Lux.

    # TODO: CLIP Schema missing for this resource.
    """

    light: Optional[LightLevelFeature] = None
    type: ResourceTypes = ResourceTypes.LIGHT_LEVEL

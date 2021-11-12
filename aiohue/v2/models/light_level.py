"""Model(s) for light_level resource on HUE bridge."""
from dataclasses import dataclass


from typing import Optional

from .resource import SensingService, ResourceTypes


@dataclass
class LightLevelFeature:
    """Represent LightLevelFeature."""

    light_level: Optional[int] = None
    light_level_valid: Optional[bool] = None


@dataclass
class LightLevel(SensingService):
    """
    Represent a LightLevel resource, a sensor reporting Illuminance in Lux.

    # TODO: CLIP Schema missing for this resource.
    """

    light: Optional[LightLevelFeature] = None
    type: ResourceTypes = ResourceTypes.LIGHT_LEVEL

"""Model(s) for light_level resource on HUE bridge."""
from dataclasses import dataclass
from types import NoneType
from typing import Optional

from .resource import SensingService, ResourceTypes


@dataclass
class LightLevelFeature:
    """Represent LightLevelFeature."""

    light_level: Optional[int] = None
    light_level_valid: bool = True


@dataclass
class LightLevel(SensingService):
    """
    Represent a LightLevel resource, a sensor reporting Illuminance in Lux.

    # TODO: CLIP Schema missing for this resource.
    """

    light: Optional[LightLevelFeature] = None
    type: ResourceTypes = ResourceTypes.LIGHT_LEVEL

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        super().__post_init__()
        if not isinstance(self.light, (NoneType, LightLevelFeature)):
            self.light = LightLevelFeature(**self.light)

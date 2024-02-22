"""
Model(s) for light_level resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_level
"""

from dataclasses import dataclass
from datetime import datetime

from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class LightLevelReport:
    """
    Represent LightLevelReport as retrieved from api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_level_get
    """

    changed: datetime
    light_level: int


@dataclass
class LightLevelFeature:
    """Represent LightLevel Feature used by Lightlevel resources."""

    light_level_report: LightLevelReport | None
    light_level: int | None = None  # deprecated
    light_level_valid: bool | None = None  # deprecated

    @property
    def value(self) -> int | None:
        """Return the actual/current value."""
        # prefer new style attribute (not available on older firmware versions)
        if self.light_level_report is not None:
            return self.light_level_report.light_level
        return self.light_level


@dataclass
class LightLevel:
    """
    Represent a (full) `LightLevel` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_level_get
    """

    id: str
    owner: ResourceIdentifier
    enabled: bool
    light: LightLevelFeature

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.LIGHT_LEVEL


@dataclass
class LightLevelPut:
    """
    LightLevel resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_level__id__put
    """

    enabled: bool | None = None

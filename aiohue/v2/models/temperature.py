"""
Model(s) for temperature resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_temperature
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class TemperatureReport:
    """
    Represent TemperatureReport as retrieved from api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_temperature_get
    """

    changed: datetime
    temperature: float


@dataclass
class TemperatureSensingFeature:
    """Represent TemperatureFeature."""

    temperature_report: Optional[TemperatureReport] = None
    temperature: Optional[float] = None  # deprecated
    temperature_valid: Optional[bool] = None  # deprecated

    @property
    def value(self) -> Optional[float]:
        """Return the actual/current value."""
        # prefer new style attribute (not available on older firmware versions)
        if self.temperature_report is not None:
            return self.temperature_report.temperature
        return self.temperature


@dataclass
class Temperature:
    """
    Represent a (full) `Temperature` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_temperature_get
    """

    id: str
    owner: ResourceIdentifier
    enabled: bool
    temperature: TemperatureSensingFeature

    id_v1: Optional[str] = None
    type: ResourceTypes = ResourceTypes.TEMPERATURE


@dataclass
class TemperaturePut:
    """
    Temperature resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_temperature__id__put
    """

    enabled: Optional[bool] = None

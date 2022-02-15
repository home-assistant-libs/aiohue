"""
Model(s) for temperature resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_temperature
"""

from dataclasses import dataclass
from typing import Optional

from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class TemperatureFeature:
    """Represent TemperatureFeature."""

    temperature: float
    temperature_valid: bool


@dataclass
class Temperature:
    """
    Represent a (full) `Temperature` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_temperature_get
    """

    id: str
    owner: ResourceIdentifier
    enabled: bool
    temperature: TemperatureFeature

    id_v1: Optional[str] = None
    type: ResourceTypes = ResourceTypes.TEMPERATURE


@dataclass
class TemperaturePut:
    """
    Temperature resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_temperature__id__put
    """

    enabled: Optional[bool] = None

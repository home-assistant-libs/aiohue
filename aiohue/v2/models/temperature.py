"""Model(s) for temperature resource on HUE bridge."""

from dataclasses import dataclass


from typing import Optional

from .resource import SensingService, ResourceTypes


@dataclass
class TemperatureFeature:
    """Represent TemperatureFeature."""

    temperature: Optional[float]
    temperature_valid: Optional[bool]


@dataclass
class Temperature(SensingService):
    """
    Represent a Temperature resource, a sensor reporting Temperature.

    TODO: CLIP Schema missing for this resource.
    """

    temperature: Optional[TemperatureFeature] = None
    type: ResourceTypes = ResourceTypes.TEMPERATURE

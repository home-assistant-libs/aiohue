"""
Model(s) for bridge resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_bridge
"""

from dataclasses import dataclass

from .resource import ResourceTypes


@dataclass
class TimeZone:
    """Represent TimeZone object as received from API."""

    time_zone: str  # e.g. Europe/Amsterdam


@dataclass
class Bridge:
    """
    Represent a (full) `Bridge` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_bridge_get
    """

    id: str
    bridge_id: str
    time_zone: TimeZone

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.BRIDGE

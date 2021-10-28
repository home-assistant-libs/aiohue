"""Model(s) for bridge resource on HUE bridge."""
from dataclasses import dataclass
from typing import Optional

from .resource import Resource, ResourceTypes


@dataclass(kw_only=True)
class TimeZone:
    """Represent TimeZone object as received from API."""

    time_zone: str  # e.g. Europe/Amsterdam


@dataclass(kw_only=True)
class Bridge(Resource):
    """
    Represent Bridge object as retrieved from the api.

    clip-api.schema.json#/definitions/BridgeGet
    """

    bridge_id: Optional[str]  # sent on get, can not be updated
    time_zone: Optional[TimeZone]
    type: ResourceTypes = ResourceTypes.BRIDGE

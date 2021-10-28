"""Model(s) for geofence_client resource on HUE bridge."""
from dataclasses import dataclass
from typing import Optional

from .resource import Resource, ResourceTypes


@dataclass(kw_only=True)
class GeofenceClient(Resource):
    """
    Representation of Geofence Client.

    clip-api.schema.json#/definitions/GeofenceClientGet
    clip-api.schema.json#/definitions/GeofenceClientPost
    clip-api.schema.json#/definitions/GeofenceClientPut
    """

    is_at_home: Optional[bool]  # Indicator if Geofence Client is at home.
    name: Optional[str]
    type: ResourceTypes = ResourceTypes.GEOFENCE_CLIENT


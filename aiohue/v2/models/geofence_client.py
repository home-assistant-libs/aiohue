"""
Model(s) for geofence_client resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_geofence_client
"""

from dataclasses import dataclass

from .resource import ResourceTypes


@dataclass
class GeofenceClient:
    """
    Represent a (full) `GeofenceClient` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_geofence_client_get
    """

    id: str
    name: str
    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.GEOFENCE_CLIENT


@dataclass
class GeofenceClientPut:
    """
    GeofenceClient resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_geofence_client__id__put
    """

    is_at_home: bool | None = None
    name: str | None = None


@dataclass
class GeofenceClientPost:
    """
    GeofenceClient resource properties that can be set with a POST request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_geofence_client_post
    """

    is_at_home: bool | None = None
    name: str | None = None
    type: ResourceTypes = ResourceTypes.GEOFENCE_CLIENT

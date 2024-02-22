"""
Model(s) for zigbee_connectivity resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zgp_connectivity
"""

from dataclasses import dataclass

from .resource import ResourceIdentifier, ResourceTypes
from .zigbee_connectivity import ConnectivityServiceStatus


@dataclass
class ZgpConnectivity:
    """
    Represent a (full) `ZgpConnectivity` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zgp_connectivity_get
    """

    id: str
    owner: ResourceIdentifier
    status: ConnectivityServiceStatus
    source_id: str
    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.ZGP_CONNECTIVITY

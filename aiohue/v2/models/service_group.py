"""
Model(s) for service_group resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_service_group
"""

from dataclasses import dataclass

from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class ServiceGroupMetadata:
    """
    Represent metadata for service group.

    Used by `service_group` resources.
    """

    name: str


@dataclass
class ServiceGroup:
    """
    Represent a (full) `ServiceGroup` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_service_group_get
    """

    id: str
    children: list[ResourceIdentifier]
    services: list[ResourceIdentifier]
    metadata: ServiceGroupMetadata

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.SERVICE_GROUP


@dataclass
class ServiceGroupPut:
    """
    ServiceGroup resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_service_group__id__put
    """

    metadata: ServiceGroupMetadata | None = None

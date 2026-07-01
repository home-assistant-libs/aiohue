"""
Model(s) for motion_area_configuration resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_motion_area_configuration
"""

from dataclasses import dataclass, field
from enum import Enum

from .resource import ResourceIdentifier, ResourceTypes


class MotionAreaHealth(Enum):
    """Enum with possible health status values."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    RECOVERING = "recovering"
    UNRECOVERABLE = "unrecoverable"
    NOT_RUNNING = "not_running"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return MotionAreaHealth.UNKNOWN


@dataclass
class MotionAreaStatus:
    """
    Represent health status information.

    Used by `motion_area_configuration` resources.
    """

    health: MotionAreaHealth = MotionAreaHealth.UNKNOWN


@dataclass
class MotionAreaParticipant:
    """
    Represent a participant in motion area configuration.

    Used by `motion_area_configuration` resources.
    """

    resource: ResourceIdentifier
    status: MotionAreaStatus = field(default_factory=MotionAreaStatus)


@dataclass
class MotionAreaConfiguration:
    """
    Represent a (full) `MotionAreaConfiguration` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_motion_area_configuration_get

    Note: Hue Bridge Pro returns a simplified schema with only `id`, `owner`, `enabled`,
    and `type`. The remaining fields are only present on standard Hue Bridges.
    """

    id: str
    enabled: bool

    # Present on Hue Bridge Pro
    owner: ResourceIdentifier | None = None

    # Present on standard Hue Bridge only
    name: str | None = None
    group: ResourceIdentifier | None = None
    participants: list[MotionAreaParticipant] | None = None
    services: list[ResourceIdentifier] | None = None
    health: MotionAreaHealth | None = None

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.MOTION_AREA_CONFIGURATION


@dataclass
class MotionAreaConfigurationPut:
    """
    MotionAreaConfiguration resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_motion_area_configuration__id__put
    """

    name: str | None = None
    enabled: bool | None = None

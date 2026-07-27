"""
Model(s) for geolocation resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_geolocation
"""

from dataclasses import dataclass
from enum import Enum

from .resource import ResourceTypes


class GeolocationDayType(Enum):
    """
    Enum with the possible day types at the configured location.

    Locations close to the poles can have days without a sunset (polar day) or
    without a sunrise (polar night), in which case `sunset_time` is meaningless.
    """

    NORMAL_DAY = "normal_day"
    POLAR_DAY = "polar_day"
    POLAR_NIGHT = "polar_night"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return GeolocationDayType.UNKNOWN


@dataclass
class GeolocationSunToday:
    """
    Represent info related to today's sun at the configured location.

    Used by `geolocation` resources.
    """

    # sunset_time: time of day in local time as `HH:MM:SS`,
    # only valid when day_type is `normal_day`.
    sunset_time: str
    day_type: GeolocationDayType


@dataclass
class Geolocation:
    """
    Represent a (full) `Geolocation` resource when retrieved from the api.

    The location is used by the bridge to resolve sunrise/sunset based automations.
    Note that the coordinates are write-only: the api accepts them in a PUT request
    but never returns them, so only the derived sun info can be read back.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_geolocation_get
    """

    id: str
    is_configured: bool

    # sun_today: only returned once the geolocation has been configured.
    sun_today: GeolocationSunToday | None = None

    type: ResourceTypes = ResourceTypes.GEOLOCATION


@dataclass
class GeolocationPut:
    """
    Geolocation resource properties that can be set/updated with a PUT request.

    The api requires both coordinates to be sent together.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_geolocation__id__put
    """

    latitude: float | None = None
    longitude: float | None = None

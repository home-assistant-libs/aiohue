"""
Model(s) for device_power resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device_power
"""

from dataclasses import dataclass
from enum import Enum

from .resource import ResourceIdentifier, ResourceTypes


class BatteryState(Enum):
    """
    Enum with all possible BatteryStates.

    - normal: battery level is sufficient
    - low: battery level low, some features might stop working, please change battery soon
    - critical: battery level critical, device can fail any moment
    """

    NORMAL = "normal"
    LOW = "low"
    CRITICAL = "critical"


@dataclass
class PowerState:
    """Represent PowerState as retrieved from api."""

    battery_level: int | None
    battery_state: BatteryState | None


@dataclass
class DevicePower:
    """
    Represent a (full) `DevicePower` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device_power_get
    """

    id: str
    owner: ResourceIdentifier
    power_state: PowerState

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.DEVICE_POWER

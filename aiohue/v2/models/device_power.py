"""
Model(s) for device_power resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device_power
"""
from dataclasses import dataclass
from enum import Enum


from typing import Optional

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

    battery_level: Optional[int]
    battery_state: Optional[BatteryState]


@dataclass
class DevicePower:
    """
    Represent a (full) `DevicePower` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_device_power_get
    """

    id: str
    owner: ResourceIdentifier
    power_state: PowerState

    id_v1: Optional[str] = None
    type: ResourceTypes = ResourceTypes.DEVICE_POWER

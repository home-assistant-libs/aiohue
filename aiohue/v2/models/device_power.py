"""Model(s) for device_power resource on HUE bridge."""
from dataclasses import dataclass
from enum import Enum


from typing import Optional, Type

from .resource import Resource, ResourceTypes


class BatteryState(Enum):
    """
    Enum with all possible BatteryStates.

    clip-api.schema.json#/definitions/TODO
    """

    UNKNOWN = "unknown"
    NORMAL = "normal"
    LOW = "low"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return BatteryState.UNKNOWN


@dataclass
class PowerState:
    """
    Represent PowerState as retrieved from api.

    clip-api.schema.json#/definitions/TODO
    """

    battery_level: Optional[int]
    battery_state: BatteryState


@dataclass
class DevicePower(Resource):
    """
    Represent a DevicePower resource, a sensor with battery state.

    clip-api.schema.json#/definitions/TODO
    """

    power_state: Optional[PowerState] = None
    type: ResourceTypes = ResourceTypes.DEVICE_POWER

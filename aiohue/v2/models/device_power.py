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

    battery_level: int
    battery_state: BatteryState

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if self.battery_state is not None and not isinstance(
            self.battery_state, BatteryState
        ):
            self.battery_state = BatteryState(self.battery_state)


@dataclass
class DevicePower(Resource):
    """
    Represent a DevicePower resource, a sensor with battery state.

    clip-api.schema.json#/definitions/TODO
    """

    power_state: Optional[PowerState] = None
    type: ResourceTypes = ResourceTypes.DEVICE_POWER

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        super().__post_init__()
        if not isinstance(self.power_state, (type(None), PowerState)):
            self.power_state = PowerState(**self.power_state)

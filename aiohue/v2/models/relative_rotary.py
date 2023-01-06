"""
Model(s) for relative_rotary resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_relative_rotary
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type

from .resource import ResourceIdentifier, ResourceTypes


class RelativeRotaryAction(Enum):
    """Enum with possible relative_rotary actions."""

    START = "start"
    REPEAT = "repeat"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: object):
        """Set default enum member if an unknown value is provided."""
        return RelativeRotaryAction.UNKNOWN


class RelativeRotaryDirection(Enum):
    """Enum with possible rotary directions."""

    CLOCK_WISE = "clock_wise"
    COUNTER_CLOCK_WISE = "counter_clock_wise"


@dataclass
class RelativeRotaryRotation:
    """
    Represent Rotation object as used by the Hue api.

    direction: required(one of clock_wise, counter_clock_wise)
    A rotation opposite to the previous rotation, will always start with new start command.

    steps: required(integer - minimum: 0 - maximum: 32767)
    amount of rotation since previous event in case of repeat,
    amount of rotation since start in case of a start_event.
    Resolution = 1000 steps / 360 degree rotation.

    duration: required(integer - minimum: 0 - maximum: 65534)
    duration of rotation since previous event in case of repeat,
    amount of rotation since start in case of a start_event. duration is specified in miliseconds.
    """

    direction: RelativeRotaryDirection
    duration: int
    steps: int


@dataclass
class RelativeRotaryEvent:
    """Represent RelativeRotaryEvent object as used by the Hue api."""

    action: RelativeRotaryAction
    rotation: RelativeRotaryRotation


@dataclass
class RelativeRotaryFeature:
    """Represent RelativeRotaryFeature object as used by the Hue api."""

    last_event: RelativeRotaryEvent


@dataclass
class RelativeRotary:
    """
    Represent a (full) `RelativeRotary` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_relative_rotary_get
    """

    id: str
    owner: ResourceIdentifier

    relative_rotary: Optional[RelativeRotaryFeature] = None
    id_v1: Optional[str] = None
    type: ResourceTypes = ResourceTypes.RELATIVE_ROTARY

"""Model(s) for button resource on HUE bridge."""
from dataclasses import dataclass
from enum import Enum
from types import NoneType
from typing import Optional, Type

from .resource import Resource, ResourceTypes


class ButtonEvent(Enum):
    """
    Enum with possible button events.

    clip-api.schema.json#/definitions/ButtonEvent
    """

    INITIAL_PRESS = "initial_press"
    REPEAT = "repeat"
    SHORT_RELEASE = "short_release"
    LONG_RELEASE = "long_release"
    DOUBLE_SHORT_RELEASE = "double_short_release"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return ButtonEvent.UNKNOWN


@dataclass
class ButtOnFeature:
    """
    Represent ButtonFeature object as received from the api.

    clip-api.schema.json#/definitions/ButtOnFeature
    """

    last_event: ButtonEvent

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.last_event, (NoneType, ButtonEvent)):
            self.last_event = ButtonEvent(self.last_event)


@dataclass
class SwitchInputMetadata:
    """
    Represent SwitchInputMetadata object as received from the api.

    clip-api.schema.json#/definitions/SwitchInputMetadata
    """

    # number of control within switch (value between 0..8).
    # Meaning in combination with type
    # - dots: Number of dots
    # - number: Number printed on device
    # - other: a logical order of controls in switch
    control_id: int


@dataclass
class Button(Resource):
    """
    Represent Button object as received from the api.

    clip-api.schema.json#/definitions/Button
    """

    metadata: Optional[SwitchInputMetadata] = None
    button: Optional[ButtOnFeature] = None
    type: ResourceTypes = ResourceTypes.BUTTON

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        super().__post_init__()
        if not isinstance(self.metadata, (NoneType, SwitchInputMetadata)):
            self.metadata = SwitchInputMetadata(**self.metadata)
        if not isinstance(self.button, (NoneType, ButtOnFeature)):
            self.button = ButtOnFeature(**self.button)

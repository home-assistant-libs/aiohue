"""
Model(s) for button resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_button
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .resource import ResourceIdentifier, ResourceTypes


class ButtonEvent(Enum):
    """Enum with possible button events."""

    INITIAL_PRESS = "initial_press"
    REPEAT = "repeat"
    SHORT_RELEASE = "short_release"
    LONG_PRESS = "long_press"
    LONG_RELEASE = "long_release"
    DOUBLE_SHORT_RELEASE = "double_short_release"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return ButtonEvent.UNKNOWN


@dataclass
class ButtonReport:
    """
    Represent ButtonReport as retrieved from api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_button_get
    """

    updated: datetime
    event: ButtonEvent


@dataclass
class ButtonFeature:
    """Represent ButtonFeature object as used by the Hue api."""

    button_report: ButtonReport | None = None
    last_event: ButtonEvent | None = None  # deprecated
    repeat_interval: int | None = None
    event_values: list[ButtonEvent] | None = None

    @property
    def value(self) -> ButtonEvent:
        """Return the actual/current value."""
        # prefer new style attribute (not available on older firmware versions)
        if self.button_report is not None:
            return self.button_report.event
        if self.last_event is not None:
            return self.last_event
        return ButtonEvent.UNKNOWN


@dataclass
class ButtonMetadata:
    """Represent ButtonMetadata object as used by the Button resource."""

    # number of control within switch (value between 0..8).
    # Meaning in combination with type
    # - dots: Number of dots
    # - number: Number printed on device
    # - other: a logical order of controls in switch
    control_id: int


@dataclass
class Button:
    """
    Represent a (full) `Button` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_button_get
    """

    id: str
    owner: ResourceIdentifier
    metadata: ButtonMetadata

    button: ButtonFeature | None = None
    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.BUTTON

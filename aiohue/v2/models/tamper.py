"""
Model(s) for tamper resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_tamper
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Type

from .resource import ResourceIdentifier, ResourceTypes


class TamperState(Enum):
    """State of a Tamper sensor."""

    TAMPERED = "tampered"
    NOT_TAMPERED = "not_tampered"


class TamperSource(Enum):
    """Source of a Tamper alert."""

    BATTERY_DOOR = "battery_door"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: Type, value: object):
        """Set default enum member if an unknown value is provided."""
        return TamperSource.UNKNOWN


@dataclass
class TamperReport:
    """
    Represent TamperReport as retrieved from api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_tamper_get
    """

    changed: datetime
    source: TamperSource
    state: TamperState


@dataclass
class Tamper:
    """
    Represent a (full) `Tamper` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_tamper_get
    """

    id: str
    owner: ResourceIdentifier
    tamper_reports: List[TamperReport] = field(default_factory=list)

    id_v1: Optional[str] = None
    type: ResourceTypes = ResourceTypes.CONTACT

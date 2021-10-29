"""Model(s) for homekit resource on HUE bridge."""
from dataclasses import dataclass, field
from enum import Enum
from types import NoneType
from typing import List, Optional

from .resource import Resource, ResourceTypes


class HomekitStatus(Enum):
    """Enum with the possible homekit status."""

    PAIRING = "pairing"
    PAIRED = "paired"
    UNPAIRED = "unpaired"


@dataclass
class HomekitGet(Resource):
    """Represent a Homekit resource object as received from the api."""

    status: Optional[HomekitStatus] = None
    status_values: List[HomekitStatus] = field(
        default_factory=HomekitStatus.__members__.values
    )
    type: ResourceTypes = ResourceTypes.HOMEKIT

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        super().__post_init__()
        if not isinstance(self.status, (NoneType, HomekitStatus)):
            self.status = HomekitStatus(self.status)
        if self.status_values and not isinstance(self.status_values[0], HomekitStatus):
            self.status_values = [HomekitStatus(x) for x in self.status]

"""Model(s) for homekit resource on HUE bridge."""
from dataclasses import dataclass, field
from enum import Enum

from typing import List, Optional

from .resource import Resource, ResourceTypes


class HomekitStatus(Enum):
    """Enum with the possible homekit status."""

    PAIRING = "pairing"
    PAIRED = "paired"
    UNPAIRED = "unpaired"


@dataclass
class HomekitGet(Resource):
    """Represent a Homekit resource object as used by the Hue api."""

    status: Optional[HomekitStatus] = None
    status_values: List[HomekitStatus] = field(
        default_factory=HomekitStatus.__members__.values
    )
    type: ResourceTypes = ResourceTypes.HOMEKIT

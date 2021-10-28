"""Model(s) for homekit resource on HUE bridge."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List

from .resource import Resource, ResourceTypes


class HomekitStatus(Enum):
    """Enum with the possible homekit status."""

    PAIRING = "pairing"
    PAIRED = "paired"
    UNPAIRED = "unpaired"


@dataclass(kw_only=True)
class HomekitGet(Resource):
    """Represent a Homekit resource object as received from the api."""

    status: HomekitStatus
    status_values: List[HomekitStatus] = field(default_factory=HomekitStatus.__members__.values)
    type: ResourceTypes = ResourceTypes.HOMEKIT

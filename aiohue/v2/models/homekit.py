"""
Model(s) for homekit resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_homekit
"""

from dataclasses import dataclass
from enum import Enum

from .resource import ResourceTypes


class HomekitStatus(Enum):
    """Enum with the possible homekit status."""

    PAIRING = "pairing"
    PAIRED = "paired"
    UNPAIRED = "unpaired"


class HomekitAction(Enum):
    """Enum with the possible homekit status."""

    NONE = ""
    RESET = "reset"
    # reset: Reset homekit, including removing all pairings and reset state and Bonjour service
    # to factory settings. The Homekit will start functioning after approximately 10 seconds.


@dataclass
class Homekit:
    """
    Represent a (full) `Homekit` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_homekit_get
    """

    id: str
    status: HomekitStatus

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.HOMEKIT


@dataclass
class HomekitPut:
    """
    Homekit resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_homekit__id__put
    """

    action: HomekitAction | None = None

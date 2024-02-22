"""
Model(s) for matter resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_matter
"""

from dataclasses import dataclass
from enum import Enum

from .resource import ResourceTypes


class MatterAction(Enum):
    """
    Enum with the possible Matter actions.

    reset: Resets Matter, including removing all fabrics and reset state to factory settings.
    """

    NONE = ""
    RESET = "reset"


@dataclass
class Matter:
    """
    Represent a (full) `Matter` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_matter_get
    """

    id: str
    max_fabrics: int  # Maximum number of fabrics that can exist at a time
    has_qr_code: bool  # Indicates whether a physical QR code is present

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.MATTER


@dataclass
class MatterPut:
    """
    Matter resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_matter__id__put
    """

    action: MatterAction | None = None

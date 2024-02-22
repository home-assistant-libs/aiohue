"""
Model(s) for contact resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_contact
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .resource import ResourceIdentifier, ResourceTypes


class ContactState(Enum):
    """State of a Contact sensor."""

    CONTACT = "contact"
    NO_CONTACT = "no_contact"


@dataclass
class ContactReport:
    """
    Represent ContactReport as retrieved from api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_contact_get
    """

    changed: datetime
    state: ContactState


@dataclass
class Contact:
    """
    Represent a (full) `Contact` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_contact_get
    """

    id: str
    owner: ResourceIdentifier
    # enabled: required(boolean)
    # true when sensor is activated, false when deactivated
    enabled: bool
    contact_report: ContactReport | None = None

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.CONTACT


@dataclass
class ContactPut:
    """
    Contact resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_contact__id__put
    """

    enabled: bool | None = None

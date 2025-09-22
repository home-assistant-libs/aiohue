"""
Model(s) for bell_button resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_bell_button
"""

from dataclasses import dataclass


from aiohue.v2.models.button import ButtonFeature, ButtonMetadata

from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class BellButton:
    """
    Represent a (full) `BellButton` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_bell_button_get
    """

    id: str
    owner: ResourceIdentifier
    metadata: ButtonMetadata

    button: ButtonFeature | None = None
    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.BELL_BUTTON

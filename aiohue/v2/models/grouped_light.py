"""Model(s) for grouped_light resource on HUE bridge."""
from dataclasses import dataclass
from typing import Optional

from .feature import AlertFeature, OnFeatureBasic
from .resource import Resource, ResourceTypes


@dataclass
class GroupedLight(Resource):
    """
    Represent a GroupedLight object as received from the api.

    clip-api.schema.json#/definitions/GroupedLightGet
    clip-api.schema.json#/definitions/GroupedLightPost
    clip-api.schema.json#/definitions/GroupedLightPut
    """

    on: Optional[OnFeatureBasic] = None
    alert: Optional[AlertFeature] = None
    type: ResourceTypes = ResourceTypes.GROUPED_LIGHT

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.on, (type(None), OnFeatureBasic)):
            self.on = OnFeatureBasic(**self.on)
        if not isinstance(self.alert, (type(None), AlertFeature)):
            self.alert = AlertFeature(**self.alert)

"""Model(s) for grouped_light resource on HUE bridge."""
from dataclasses import dataclass
from types import NoneType
from typing import Optional

from .feature import AlertFeature, OnFeatureBasic
from .resource import Resource, ResourceTypes


@dataclass
class GroupedLight(Resource):
    """
    Represent a GroupedLight object as used by the Hue api.

    clip-api.schema.json#/definitions/GroupedLightGet
    clip-api.schema.json#/definitions/GroupedLightPost
    clip-api.schema.json#/definitions/GroupedLightPut
    """

    on: Optional[OnFeatureBasic] = None
    alert: Optional[AlertFeature] = None
    type: ResourceTypes = ResourceTypes.GROUPED_LIGHT

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        super().__post_init__()
        if not isinstance(self.on, (NoneType, OnFeatureBasic)):
            self.on = OnFeatureBasic(**self.on)
        if not isinstance(self.alert, (NoneType, AlertFeature)):
            self.alert = AlertFeature(**self.alert)

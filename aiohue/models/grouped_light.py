"""Model(s) for grouped_light resource on HUE bridge."""
from dataclasses import dataclass
from typing import Optional

from .feature import AlertFeature, OnFeatureBasic
from .resource import Resource, ResourceTypes


@dataclass(kw_only=True)
class GroupedLight(Resource):
    """
    Represent a GroupedLight object as received from the api.

    clip-api.schema.json#/definitions/GroupedLightGet
    clip-api.schema.json#/definitions/GroupedLightPost
    clip-api.schema.json#/definitions/GroupedLightPut
    """

    on: Optional[OnFeatureBasic]
    alert: Optional[AlertFeature]
    type: ResourceTypes = ResourceTypes.GROUPED_LIGHT


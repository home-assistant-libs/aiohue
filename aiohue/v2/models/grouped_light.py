"""Model(s) for grouped_light resource on HUE bridge."""
from dataclasses import dataclass

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

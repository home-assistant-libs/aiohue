"""Model(s) for Scene resource on HUE bridge."""
from dataclasses import dataclass
from typing import List, Optional

from .feature import (
    ColorFeatureBasic,
    ColorTemperatureFeatureBasic,
    DimmingFeatureBasic,
    OnFeatureBasic,
    RecallFeature,
)
from .resource import (
    Resource,
    ResourceIdentifier,
    ResourceTypes,
)


@dataclass(kw_only=True)
class ActionAction:
    """
    Represent ActionAction object as received from the api.

    The action to be executed on recall.
    clip-api.schema.json#/definitions/ActionAction
    clip-api.schema.json#/definitions/ActionActionPost
    clip-api.schema.json#/definitions/ActionActionPut
    """

    on: Optional[OnFeatureBasic]
    dimming: Optional[DimmingFeatureBasic]
    color: Optional[ColorFeatureBasic]
    color_temperature: Optional[ColorTemperatureFeatureBasic]


@dataclass(kw_only=True)
class Action:
    """
    Represent Action object as received from the api.

    clip-api.schema.json#/definitions/ActionGet
    clip-api.schema.json#/definitions/ActionPut
    clip-api.schema.json#/definitions/ActionPost
    """

    target: ResourceIdentifier
    action: ActionAction


@dataclass(kw_only=True)
class SceneMetadata:
    """
    Represent SceneMetadata object as received from the api.

    clip-api.schema.json#/definitions/SceneMetadataGet
    clip-api.schema.json#/definitions/SceneMetadataPost
    clip-api.schema.json#/definitions/SceneMetadataPut
    """

    name: str
    image: Optional[ResourceIdentifier]


@dataclass(kw_only=True)
class SceneService(Resource):
    """
    Represent SceneService object as received from the api.

    clip-api.schema.json#/definitions/SceneServiceGet
    clip-api.schema.json#/definitions/SceneServicePost
    clip-api.schema.json#/definitions/SceneServicePut
    """

    actions: Optional[List[Action]]
    recall: Optional[RecallFeature]  # used only on update/set


@dataclass(kw_only=True)
class Scene(SceneService):
    """
    Represent Scene object as received from the api.

    Inherited from SceneService.
    clip-api.schema.json#/definitions/SceneGet
    clip-api.schema.json#/definitions/ScenePost
    clip-api.schema.json#/definitions/ScenePut
    """

    group: Optional[ResourceIdentifier]
    metadata: Optional[SceneMetadata]
    speed: Optional[float] # optional transition speed
    type: ResourceTypes = ResourceTypes.SCENE

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


@dataclass
class ActionAction:
    """
    Represent ActionAction object as received from the api.

    The action to be executed on recall.
    clip-api.schema.json#/definitions/ActionAction
    clip-api.schema.json#/definitions/ActionActionPost
    clip-api.schema.json#/definitions/ActionActionPut
    """

    on: Optional[OnFeatureBasic] = None
    dimming: Optional[DimmingFeatureBasic] = None
    color: Optional[ColorFeatureBasic] = None
    color_temperature: Optional[ColorTemperatureFeatureBasic] = None


@dataclass
class Action:
    """
    Represent Action object as received from the api.

    clip-api.schema.json#/definitions/ActionGet
    clip-api.schema.json#/definitions/ActionPut
    clip-api.schema.json#/definitions/ActionPost
    """

    target: ResourceIdentifier
    action: ActionAction


@dataclass
class SceneMetadata:
    """
    Represent SceneMetadata object as received from the api.

    clip-api.schema.json#/definitions/SceneMetadataGet
    clip-api.schema.json#/definitions/SceneMetadataPost
    clip-api.schema.json#/definitions/SceneMetadataPut
    """

    name: str
    image: Optional[ResourceIdentifier]


@dataclass
class SceneService(Resource):
    """
    Represent SceneService object as received from the api.

    clip-api.schema.json#/definitions/SceneServiceGet
    clip-api.schema.json#/definitions/SceneServicePost
    clip-api.schema.json#/definitions/SceneServicePut
    """

    actions: Optional[List[Action]] = None
    recall: Optional[RecallFeature] = None  # used only on update/set


@dataclass
class Scene(SceneService):
    """
    Represent Scene object as received from the api.

    Inherited from SceneService.
    clip-api.schema.json#/definitions/SceneGet
    clip-api.schema.json#/definitions/ScenePost
    clip-api.schema.json#/definitions/ScenePut
    """

    group: Optional[ResourceIdentifier] = None
    metadata: Optional[SceneMetadata] = None
    speed: Optional[float] = None  # optional transition speed
    type: ResourceTypes = ResourceTypes.SCENE

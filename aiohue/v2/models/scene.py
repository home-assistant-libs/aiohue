"""
Model(s) for Scene resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_scene
"""
from dataclasses import dataclass
from typing import List, Optional

from .feature import (
    ColorFeatureBase,
    ColorTemperatureFeatureBase,
    DimmingFeatureBase,
    GradientFeatureBase,
    OnFeature,
    PaletteFeature,
    RecallFeature,
)
from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class ActionAction:
    """Represent (scene) `ActionAction` model."""

    on: Optional[OnFeature] = None
    dimming: Optional[DimmingFeatureBase] = None
    color: Optional[ColorFeatureBase] = None
    color_temperature: Optional[ColorTemperatureFeatureBase] = None
    gradient: Optional[GradientFeatureBase] = None


@dataclass
class Action:
    """Represent (scene) `Action` model."""

    target: ResourceIdentifier
    action: ActionAction


@dataclass
class SceneMetadata:
    """Represent SceneMetadata object as used by the Hue api."""

    name: str
    image: Optional[ResourceIdentifier] = None


@dataclass
class SceneMetadataPut:
    """Represent SceneMetadata model when sent/updated to the API with PUT request."""

    name: str


@dataclass
class Scene:
    """
    Represent (full) `Scene` Model when retrieved from the API.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_scene__id__get
    """

    id: str
    metadata: SceneMetadata
    # group: required(object)
    # Group associated with this Scene. All services in the group are part of this scene.
    # If the group is changed the scene is updated (e.g. light added/removed)
    group: ResourceIdentifier
    # actions: required(array of Action)
    # List of actions to be executed synchronously on recal
    actions: List[Action]
    palette: PaletteFeature
    # speed: required(number – minimum: 0 – maximum: 1)
    speed: float

    # optional params
    id_v1: Optional[str] = None

    type: ResourceTypes = ResourceTypes.SCENE


@dataclass
class ScenePut:
    """
    Properties to send when updating/setting a `Scene` object on the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_scene__id__put
    """

    metadata: Optional[SceneMetadataPut] = None
    actions: Optional[List[Action]] = None
    palette: Optional[PaletteFeature] = None
    recall: Optional[RecallFeature] = None
    palette: Optional[PaletteFeature] = None
    # speed: (number – minimum: 0 – maximum: 1)
    # Speed of dynamic palette for this scene
    speed: Optional[float] = None


@dataclass
class ScenePost:
    """
    Properties to send when creating a `Scene` object on the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_scene_post
    """

    metadata: SceneMetadata
    group: ResourceIdentifier
    actions: List[Action]
    palette: Optional[PaletteFeature] = None
    speed: Optional[float] = None
    type: ResourceTypes = ResourceTypes.SCENE

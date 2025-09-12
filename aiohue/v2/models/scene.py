"""
Model(s) for Scene resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_scene
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .feature import (
    ColorFeatureBase,
    ColorTemperatureFeatureBase,
    DimmingFeatureBase,
    DynamicsFeaturePut,
    GradientFeatureBase,
    OnFeature,
    PaletteFeature,
    RecallFeature,
    SceneEffectsFeature,
)
from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class ActionAction:
    """Represent (scene) `ActionAction` model."""

    on: OnFeature | None = None
    dimming: DimmingFeatureBase | None = None
    color: ColorFeatureBase | None = None
    color_temperature: ColorTemperatureFeatureBase | None = None
    gradient: GradientFeatureBase | None = None
    effects: SceneEffectsFeature | None = None
    dynamics: DynamicsFeaturePut | None = None


@dataclass
class Action:
    """Represent (scene) `Action` model."""

    target: ResourceIdentifier
    action: ActionAction


@dataclass
class SceneMetadata:
    """Represent SceneMetadata object as used by the Hue api."""

    name: str
    image: ResourceIdentifier | None = None


class SceneActiveStatus(Enum):
    """Enum with possible active statuses for a Scene.

    Hue API docs (resource: scene / status.active):
    - inactive
    - static
    - dynamic_palette
    """

    INACTIVE = "inactive"
    STATIC = "static"
    DYNAMIC_PALETTE = "dynamic_palette"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Return default member if unknown value encountered."""
        return SceneActiveStatus.UNKNOWN


@dataclass
class SceneStatus:
    """Represent Scene Status object.

    Consists of information about the current status and last time the scene was recalled.
    Hue API fields:
        - active: one of inactive | static | dynamic_palette
        - last_recall: ISO 8601 timestamp (optional if never recalled)
    """

    active: SceneActiveStatus
    last_recall: datetime | None = None


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
    # List of actions to be executed synchronously on recall
    actions: list[Action]
    # speed: required(number – minimum: 0 – maximum: 1)
    speed: float
    # auto_dynamic: whether to automatically start the scene dynamically on active recall
    auto_dynamic: bool | None = None
    # status: the current active status and last recall of the scene
    status: SceneStatus | None = None

    # optional params
    id_v1: str | None = None
    palette: PaletteFeature | None = None

    type: ResourceTypes = ResourceTypes.SCENE


@dataclass
class ScenePut:
    """
    Properties to send when updating/setting a `Scene` object on the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_scene__id__put
    """

    metadata: SceneMetadataPut | None = None
    actions: list[Action] | None = None
    palette: PaletteFeature | None = None
    recall: RecallFeature | None = None
    palette: PaletteFeature | None = None
    # speed: (number – minimum: 0 – maximum: 1)
    # Speed of dynamic palette for this scene
    speed: float | None = None
    auto_dynamic: bool | None = None


@dataclass
class ScenePost:
    """
    Properties to send when creating a `Scene` object on the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_scene_post
    """

    metadata: SceneMetadata
    group: ResourceIdentifier
    actions: list[Action]
    palette: PaletteFeature | None = None
    speed: float | None = None
    auto_dynamic: bool | None = None
    type: ResourceTypes = ResourceTypes.SCENE

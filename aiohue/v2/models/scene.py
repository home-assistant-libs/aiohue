"""Model(s) for Scene resource on HUE bridge."""
from dataclasses import dataclass
from types import NoneType
from typing import List, Optional

from .feature import (
    ColorFeatureBasic,
    ColorTemperatureFeatureBasic,
    DimmingFeatureBasic,
    OnFeatureBasic,
    PaletteFeature,
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
    Represent ActionAction object as used by the Hue api.

    The action to be executed on recall.
    clip-api.schema.json#/definitions/ActionAction
    clip-api.schema.json#/definitions/ActionActionPost
    clip-api.schema.json#/definitions/ActionActionPut
    """

    on: Optional[OnFeatureBasic] = None
    dimming: Optional[DimmingFeatureBasic] = None
    color: Optional[ColorFeatureBasic] = None
    color_temperature: Optional[ColorTemperatureFeatureBasic] = None

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.on, (NoneType, OnFeatureBasic)):
            self.on = OnFeatureBasic(**self.on)
        if not isinstance(self.dimming, (NoneType, DimmingFeatureBasic)):
            self.dimming = DimmingFeatureBasic(**self.dimming)
        if not isinstance(
            self.color_temperature, (NoneType, ColorTemperatureFeatureBasic)
        ):
            self.color_temperature = ColorTemperatureFeatureBasic(
                **self.color_temperature
            )
        if not isinstance(self.color, (NoneType, ColorFeatureBasic)):
            self.color = ColorFeatureBasic(**self.color)


@dataclass
class Action:
    """
    Represent Action object as used by the Hue api.

    clip-api.schema.json#/definitions/ActionGet
    clip-api.schema.json#/definitions/ActionPut
    clip-api.schema.json#/definitions/ActionPost
    """

    target: ResourceIdentifier
    action: ActionAction

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.target, ResourceIdentifier):
            self.target = ResourceIdentifier(**self.target)
        if not isinstance(self.action, ActionAction):
            self.action = ActionAction(**self.action)


@dataclass
class SceneMetadata:
    """
    Represent SceneMetadata object as used by the Hue api.

    clip-api.schema.json#/definitions/SceneMetadataGet
    clip-api.schema.json#/definitions/SceneMetadataPost
    clip-api.schema.json#/definitions/SceneMetadataPut
    """

    name: str
    image: Optional[ResourceIdentifier] = None

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if not isinstance(self.image, (NoneType, ResourceIdentifier)):
            self.image = ResourceIdentifier(**self.image)


@dataclass
class SceneService(Resource):
    """
    Represent SceneService object as used by the Hue api.

    clip-api.schema.json#/definitions/SceneServiceGet
    clip-api.schema.json#/definitions/SceneServicePost
    clip-api.schema.json#/definitions/SceneServicePut
    """

    actions: Optional[List[Action]] = None
    recall: Optional[RecallFeature] = None  # used only on update/set

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        super().__post_init__()
        if self.actions and self.recall:
            raise ValueError("actions and recall can not be set at the same time")
        if not isinstance(self.recall, (NoneType, RecallFeature)):
            self.recall = RecallFeature(**self.recall)
        if self.actions and not isinstance(self.actions[0], Action):
            self.actions = [Action(**x) for x in self.actions]


@dataclass
class Scene(SceneService):
    """
    Represent Scene object as used by the Hue api.

    Inherited from SceneService.
    clip-api.schema.json#/definitions/SceneGet
    clip-api.schema.json#/definitions/ScenePost
    clip-api.schema.json#/definitions/ScenePut
    """

    group: Optional[ResourceIdentifier] = None
    metadata: Optional[SceneMetadata] = None
    # speed: current transition speed (readonly)
    speed: Optional[float] = None
    palette: Optional[PaletteFeature] = None
    type: ResourceTypes = ResourceTypes.SCENE

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        super().__post_init__()
        if not isinstance(self.group, (NoneType, ResourceIdentifier)):
            self.group = ResourceIdentifier(**self.group)
        if not isinstance(self.metadata, (NoneType, SceneMetadata)):
            self.metadata = SceneMetadata(**self.metadata)
        if not isinstance(self.palette, (NoneType, PaletteFeature)):
            self.palette = PaletteFeature(**self.palette)

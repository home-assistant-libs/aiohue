"""
Model(s) for Smart Scene resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_smart_scene
"""

from dataclasses import dataclass
from enum import Enum

from .resource import ResourceIdentifier, ResourceTypes
from .scene import SceneMetadata, SceneMetadataPut


class WeekDay(Enum):
    """Represent Day of Week in TimeSlot."""

    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"


class SmartSceneState(Enum):
    """The state of the Active Scene."""

    ACTIVE = "active"
    INACTIVE = "inactive"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return SmartSceneState.INACTIVE


@dataclass
class TimeslotStartTimeTime:
    """Time object."""

    hour: int  # minimum: 0 – maximum: 23
    minute: int  # minimum: 0 – maximum: 59
    second: int  # minimum: 0 – maximum: 59

    def __post_init__(self):
        """Validate values."""
        if self.hour < 0 or self.hour > 23:
            raise ValueError("Hour must be a value within range of 0 and 23")
        if self.minute < 0 or self.minute > 59:
            raise ValueError("Minute must be a value within range of 0 and 59")
        if self.second < 0 or self.second > 59:
            raise ValueError("Second must be a value within range of 0 and 59")


@dataclass
class TimeslotStartTime:
    """Representation of a Start time object within a timeslot."""

    kind: str  # currently fixed to 'time'
    time: TimeslotStartTimeTime


@dataclass
class SmartSceneTimeslot:
    """
    Represent SmartSceneTimeslot as used by Smart Scenes.

    Information on what is the light state for every timeslot of the day.
    """

    start_time: TimeslotStartTime
    target: ResourceIdentifier


@dataclass
class DayTimeSlots:
    """Represent DayTimeSlots information, used by Smart Scenes."""

    timeslots: list[SmartSceneTimeslot]
    recurrence: list[WeekDay]


@dataclass
class SmartSceneActiveTimeslot:
    """The active time slot in execution."""

    timeslot_id: int
    weekday: WeekDay


class SmartSceneRecallAction:
    """
    Enum with possible recall actions for smart scenes.

    Activate will start the smart (24h) scene; deactivate will stop it.
    """

    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"


@dataclass
class SmartSceneRecall:
    """Properties to send when activating a Smart Scene."""

    action: SmartSceneRecallAction


@dataclass
class SmartScene:
    """
    Represent (full) `SmartScene` Model when retrieved from the API.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_smart_scene__id__get
    """

    id: str
    metadata: SceneMetadata
    # group: required(object)
    # Group associated with this Scene. All services in the group are part of this scene.
    # If the group is changed the scene is updated (e.g. light added/removed)
    group: ResourceIdentifier
    # actions: required(array of Action)
    # List of actions to be executed synchronously on recall
    week_timeslots: list[DayTimeSlots]
    # state: the current state of the smart scene.
    # The default state is inactive if no recall is provided
    state: SmartSceneState

    # optional params

    # active_timeslot: information on what is the light state for every timeslot of the day
    active_timeslot: SmartSceneActiveTimeslot | None = None
    id_v1: str | None = None

    type: ResourceTypes = ResourceTypes.SMART_SCENE


@dataclass
class SmartScenePut:
    """
    Properties to send when updating/setting a `SmartScene` object on the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_smart_scene__id__put
    """

    metadata: SceneMetadataPut | None = None
    week_timeslots: list[DayTimeSlots] | None = None
    recall: SmartSceneRecall | None = None


@dataclass
class SmartSceneScenePost:
    """
    Properties to send when creating a `SmartScene` object on the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_smarft_scene_post
    """

    metadata: SceneMetadata
    group: ResourceIdentifier
    week_timeslots: list[DayTimeSlots]
    recall: SmartSceneRecall | None = None
    type: ResourceTypes = ResourceTypes.SMART_SCENE

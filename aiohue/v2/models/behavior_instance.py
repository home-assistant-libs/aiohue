"""
Model(s) for behavior_instance resource on HUE bridge.

API to manage instances of script.
https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_behavior_instance
"""

from dataclasses import dataclass
from enum import Enum

from .resource import ResourceIdentifier, ResourceTypes


class BehaviorInstanceStatus(Enum):
    """Behavior script instance status."""

    INITIALIZING = "initializing"
    RUNNING = "running"
    DISABLED = "disabled"
    ERRORED = "errored"


@dataclass
class BehaviorInstanceMetadata:
    """Represent BehaviorInstance Metadata object as used by BehaviorInstance resource."""

    name: str | None = None


class DependencyLevel(Enum):
    """
    Enum with dependency Levels.

    - non_critical: Defines a dependency between resources:
      although source is impacted by removal of target, source remains
      of target means removal of source.
    - critical: Defines a critical dependency between resources:
      source cannot function without target,
      hence removal of target means removal of source.
    """

    NON_CRITICAL = "non_critical"
    CRITICAL = "critical"


@dataclass
class ResourceDependee:
    """
    ResourceDependee object as used by the Hue api.

    Represents a resource which (this) resource is dependent on.

    clip-api.schema.json#/definitions/ResourceDependeeGet
    """

    # target: required(object - Id of the dependency resource (target).
    target: ResourceIdentifier
    level: DependencyLevel
    type: str | None = None


@dataclass
class BehaviorInstance:
    """
    Represent a (full) `BehaviorInstance` resource when retrieved from the api.

    BehaviorInstance is an instance of a script.
    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_behavior_instance_get
    """

    id: str
    script_id: str
    enabled: bool

    # configuration: required(object)
    # Script configuration.
    # This property is validated using ScriptDefinition.configuration_schema JSON schema.
    configuration: dict

    # dependees: required(array of ResourceDependee)
    # Represents all resources which this instance depends on.
    dependees: list[ResourceDependee]

    # status: required(one of initializing, running, disabled, errored)
    # If the script is in the errored state then check errors for more details about the error.
    status: BehaviorInstanceStatus

    # last_error: required(string) - Last error happened while executing the script.
    last_error: str
    metadata: BehaviorInstanceMetadata

    # state: (object)
    # Script instance state.
    # This read-only property is according to ScriptDefinition.state_schema JSON schema.
    state: dict | None = None

    id_v1: str | None = None
    migrated_from: str | None = None
    type: ResourceTypes = ResourceTypes.BEHAVIOR_INSTANCE


@dataclass
class BehaviorInstancePut:
    """
    Properties to send when updating/setting a `BehaviorInstance` object on the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_behavior_instance__put
    """

    enabled: bool | None = None
    # configuration: (object) Script configuration.
    # This property is validated using ScriptDefinition.configuration_schema JSON schema.
    configuration: dict | None = None
    # trigger: (object) Action that needs to be taken by this script instance.
    # This property is validated using ScriptDefinition.trigger_schema JSON schema.
    trigger: dict | None = None
    metadata: BehaviorInstanceMetadata | None = None


@dataclass
class BehaviorInstancePost:
    """
    Properties to send when creating a `BehaviorInstance` object on the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#behavior_instance_post
    """

    script_id: str
    enabled: bool
    configuration: dict
    metadata: BehaviorInstanceMetadata | None = None
    migrated_from: str | None = None

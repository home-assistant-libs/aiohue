"""Dependency Schemas used by (script) Hue resources."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .resource import Resource, ResourceIdentifier, ResourceTypes


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
class DependencyGet:
    """
    Dependency object as received from the api.

    Defines target resource of a dependency.

    clip-api.schema.json#/definitions/DependencyGet
    """

    target: ResourceIdentifier  # Id of the dependency resource (target).
    level: DependencyLevel
    type: Optional[str] = None

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        if self.target is not None and not isinstance(self.target, ResourceIdentifier):
            self.target = ResourceIdentifier(**self.target)
        if self.level is not None and not isinstance(self.level, DependencyLevel):
            self.level = DependencyLevel(**self.level)


@dataclass
class ResourceDependeeGet(DependencyGet):
    """
    ResourceDependee object as received from the api.

    Represents a resource which (this) resource is dependent on.

    clip-api.schema.json#/definitions/ResourceDependeeGet
    """


@dataclass
class ResourceDependerGet(DependencyGet):
    """
    ResourceDepender object as received from the api.

    Represents a resource which depend on (this) resource.

    clip-api.schema.json#/definitions/ResourceDependerGet
    """


@dataclass
class DependerGet(Resource):
    """
    Depender object as received from the api.

    Represents all the resources which depend on a resource.

    clip-api.schema.json#/definitions/DependerGet
    """

    dependers: List[ResourceDependerGet] = field(default_factory=list)
    type: ResourceTypes = ResourceTypes.DEPENDER

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        super().__post_init__()
        if self.dependers and not isinstance(self.dependers[0], ResourceDependerGet):
            self.dependers = [ResourceDependerGet(**x) for x in self.dependers]

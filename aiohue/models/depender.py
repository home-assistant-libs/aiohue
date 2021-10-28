"""Dependency Schemas used by (script) Hue resources."""

from dataclasses import dataclass
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


@dataclass(kw_only=True)
class DependencyGet:
    """
    Dependency object as received from the api.

    Defines target resource of a dependency.

    clip-api.schema.json#/definitions/DependencyGet
    """

    target: ResourceIdentifier  # Id of the dependency resource (target).
    level: DependencyLevel
    type: Optional[str]


@dataclass(kw_only=True)
class ResourceDependeeGet(DependencyGet):
    """
    ResourceDependee object as received from the api.

    Represents a resource which (this) resource is dependent on.

    clip-api.schema.json#/definitions/ResourceDependeeGet
    """


@dataclass(kw_only=True)
class ResourceDependerGet(DependencyGet):
    """
    ResourceDepender object as received from the api.

    Represents a resource which depend on (this) resource.

    clip-api.schema.json#/definitions/ResourceDependerGet
    """


@dataclass(kw_only=True)
class DependerGet(Resource):
    """
    Depender object as received from the api.

    Represents all the resources which depend on a resource.

    clip-api.schema.json#/definitions/DependerGet
    """

    dependers: List[ResourceDependerGet]
    type: ResourceTypes = ResourceTypes.DEPENDER

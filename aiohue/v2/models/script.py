"""Model(s) for script resource on HUE bridge."""
from dataclasses import dataclass


from typing import List, Optional

from .depender import ResourceDependeeGet
from .resource import Resource, ResourceMetadata, ResourceTypes


@dataclass
class ScriptMetadata(ResourceMetadata):
    """
    Represent ScriptMetadata object as used by the Hue api.

    clip-api.schema.json#/definitions/ScriptMetadataGet
    """

    name: Optional[str] = None


@dataclass
class ScriptDefinition(Resource):
    """
    Represent SceneService object as used by the Hue api.

    Definition of a script.
    clip-api.schema.json#/definitions/ScriptDefinitionGet
    """

    type: Optional[ResourceTypes]
    # Short description of script.
    description: Optional[str] = None
    # The configuration object is a JSON scheme that describes
    # the configuration needed to instantiate the script.
    configuration: Optional[dict] = None
    # version of the script
    version: Optional[str] = None
    metadata: Optional[ScriptMetadata] = None


@dataclass
class InstanceMetadata:
    """
    Represent InstanceMetadata object as used by the Hue api.

    Metadata for ScriptInstance.

    clip-api.schema.json#/definitions/InstanceMetadata
    """

    name: Optional[str] = None  # optional in get/post


@dataclass
@dataclass
class ScriptInstance(Resource):
    """
    Represent ScriptInstance object as used by the Hue api.

    Representation of active script.
    Scripts are instantiated using the id and configuration of the ScriptDefinition.

    clip-api.schema.json#/definitions/ScriptInstanceGet
    clip-api.schema.json#/definitions/ScriptInstancePost
    clip-api.schema.json#/definitions/ScriptInstancePut
    """

    # Identifier to ScriptDefinition.
    script_id: Optional[str] = None  # can not be set in post/put
    # Indicated whether a scripts is enabled.
    enabled: Optional[bool] = None
    # State of the instance according json-schema in corresponding
    # state attribute in the ScriptDefinition.
    state: Optional[dict] = None
    # Configuration of the script according json-schema in corresponding
    # config attribute in the ScriptDefinition.
    configuration: Optional[dict] = None
    # Represents all resources which this instance depends on.
    dependees: Optional[List[ResourceDependeeGet]] = None
    status: Optional[str] = None
    status_data: Optional[dict] = None
    metadata: Optional[InstanceMetadata] = None
    type: Optional[ResourceTypes] = None

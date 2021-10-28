"""Model(s) for script resource on HUE bridge."""
from dataclasses import dataclass
from typing import List, Optional

from .depender import ResourceDependeeGet
from .resource import Resource, ResourceTypes


@dataclass(kw_only=True)
class ScriptMetadata(Resource):
    """
    Represent ScriptMetadata object as received from the api.

    clip-api.schema.json#/definitions/ScriptMetadataGet
    """

    name: str


@dataclass(kw_only=True)
class ScriptDefinition(Resource):
    """
    Represent SceneService object as received from the api.

    Definition of a script.
    clip-api.schema.json#/definitions/ScriptDefinitionGet
    """

    type: Optional[ResourceTypes]
    # Short description of script.
    description: str
    # The configuration object is a JSON scheme that describes
    # the configuration needed to instantiate the script.
    configuration: dict
    # version of the script
    version: str
    metadata: ScriptMetadata


@dataclass(kw_only=True)
class InstanceMetadata:
    """
    Represent InstanceMetadata object as received from the api.

    Metadata for ScriptInstance.

    clip-api.schema.json#/definitions/InstanceMetadata
    """

    name: Optional[str]  # optional in get/post


@dataclass(kw_only=True)
@dataclass(kw_only=True)
class ScriptInstance(Resource):
    """
    Represent ScriptInstance object as received from the api.

    Representation of active script.
    Scripts are instantiated using the id and configuration of the ScriptDefinition.

    clip-api.schema.json#/definitions/ScriptInstanceGet
    clip-api.schema.json#/definitions/ScriptInstancePost
    clip-api.schema.json#/definitions/ScriptInstancePut
    """

    # Identifier to ScriptDefinition.
    script_id: Optional[str]  # can not be set in post/put
    # Indicated whether a scripts is enabled.
    enabled: Optional[bool]
    # State of the instance according json-schema in corresponding
    # state attribute in the ScriptDefinition.
    state: Optional[dict]
    # Configuration of the script according json-schema in corresponding
    # config attribute in the ScriptDefinition.
    configuration: Optional[dict]
    # Represents all resources which this instance depends on.
    dependees: Optional[List[ResourceDependeeGet]]
    status: Optional[str]
    status_data: Optional[dict]
    metadata: Optional[InstanceMetadata]
    type: Optional[ResourceTypes]

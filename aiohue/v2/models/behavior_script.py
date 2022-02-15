"""
Model(s) for behavior_script resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_behavior_script
"""
from dataclasses import dataclass
from typing import Optional

from .resource import ResourceTypes


@dataclass
class BehaviorScriptMetadata:
    """Represent BehaviorScript Metadata object as used by BehaviorScript resource."""

    name: Optional[str] = None


@dataclass
class BehaviorScript:
    """
    Represent a (full) `Button` resource when retrieved from the api.

    Available scripts that can be instantiated.
    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_behavior_script_get
    """

    id: str
    description: str
    # configuration_schema: required(object)
    # JSON schema object used for validating ScriptInstance.configuration property.
    configuration_schema: dict
    # trigger_schema: required(object)
    # JSON schema object used for validating ScriptInstance.trigger property.
    trigger_schema: dict
    # state_schema: required(object)
    # JSON schema of ScriptInstance.state property.
    state_schema: dict
    version: str

    id_v1: Optional[str] = None
    type: ResourceTypes = ResourceTypes.BEHAVIOR_SCRIPT

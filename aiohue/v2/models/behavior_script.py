"""
Model(s) for behavior_script resource on HUE bridge.

API to discover available scripts that can be instantiated
https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_behavior_script
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Type

from .resource import ResourceTypes


class BehaviorScriptCategory:
    """Enum with various Bahavior Script Categories."""

    AUTOMATION = "automation"
    ENTERTAINMENT = "entertainment"
    ACCESSORY = "accessory"
    OTHER = "other"

    @classmethod
    def _missing_(cls: Type, value: str):
        """Set default enum member if an unknown value is provided."""
        return BehaviorScriptCategory.OTHER


@dataclass
class BehaviorScriptMetadata:
    """Represent BehaviorScript Metadata object as used by BehaviorScript resource."""

    name: Optional[str] = None
    category: BehaviorScriptCategory = BehaviorScriptCategory.OTHER


@dataclass
class BehaviorScript:
    """
    Represent a (full) `BehaviorScript` resource when retrieved from the api.

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
    metadata: BehaviorScriptMetadata
    supported_features: Optional[List[str]]
    max_number_instances: Optional[int] = None

    id_v1: Optional[str] = None
    type: ResourceTypes = ResourceTypes.BEHAVIOR_SCRIPT

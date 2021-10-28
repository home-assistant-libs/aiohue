"""Model(s) for behavior_script resource on HUE bridge."""
from dataclasses import dataclass

from .resource import ResourceTypes
from .script import ScriptDefinition


@dataclass(kw_only=True)
class BehaviorScript(ScriptDefinition):
    """
    Represent BehaviorScript object as received from the api.

    clip-api.schema.json#/definitions/BehaviorScriptGet
    """

    type: ResourceTypes = ResourceTypes.BEHAVIOR_SCRIPT

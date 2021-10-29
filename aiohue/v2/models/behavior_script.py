"""Model(s) for behavior_script resource on HUE bridge."""
from dataclasses import dataclass

from .resource import ResourceTypes
from .script import ScriptDefinition


@dataclass
class BehaviorScript(ScriptDefinition):
    """
    Represent BehaviorScript object as used by the Hue api.

    clip-api.schema.json#/definitions/BehaviorScriptGet
    """

    type: ResourceTypes = ResourceTypes.BEHAVIOR_SCRIPT

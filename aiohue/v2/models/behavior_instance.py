"""Model(s) for behavior_instance (automation) resource on HUE bridge."""
from dataclasses import dataclass

from .resource import ResourceTypes
from .script import ScriptInstance


@dataclass
class BehaviorInstance(ScriptInstance):
    """
    Represent BehaviorInstance object as used by the Hue api.

    clip-api.schema.json#/definitions/BehaviorInstanceGet
    clip-api.schema.json#/definitions/BehaviorInstancePost
    clip-api.schema.json#/definitions/BehaviorInstancePut
    """

    type: ResourceTypes = ResourceTypes.BEHAVIOR_INSTANCE

"""
Model(s) for clip resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_clip
"""

from dataclasses import dataclass

from .resource import ResourceTypes


@dataclass
class Clip:
    """
    Represent a (full) `Clip` resource when retrieved from the api.

    Capability discovery resource: it enumerates every public resource type the
    bridge serves, so a client can detect optional features (Hue Secure, speakers,
    MotionAware, ...) without probing the individual endpoints.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_clip_get
    """

    id: str
    # NOTE: deliberately kept as raw strings instead of `ResourceTypes`.
    # The whole point of this resource is to reveal types a client may not know
    # yet and the enum collapses every one of those into a single UNKNOWN member.
    resources: list[str]

    type: ResourceTypes = ResourceTypes.CLIP

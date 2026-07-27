"""
Model(s) for entertainment resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_entertainment
"""

from dataclasses import dataclass

from .entertainment_configuration import Segment
from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class SegmentationProperties:
    """
    Represent a SegmentationProperties dict type.

    All properties regarding the segment capabilities of this device:
    the configuratibility, max_segments and all segment tables.
    """

    configurable: bool
    max_segments: int
    segments: list[Segment]


@dataclass
class Entertainment:
    """
    Represent a (full) `Entertainment` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_entertainment_get
    """

    id: str
    owner: ResourceIdentifier
    # renderer: Indicates if a lamp can be used for entertainment streaming as renderer
    renderer: bool
    # proxy: Indicates if a lamp can be used for entertainment streaming as a proxy node
    proxy: bool
    # renderer_reference: Indicates which light service is linked to this
    # entertainment service
    renderer_reference: ResourceIdentifier | None = None
    # equalizer: Indicates if a lamp can handle the equalization factor to dimming
    # maximum brightness in a stream
    equalizer: bool | None = None
    # max_streams: (integer – minimum: 1)
    # Indicates the maximum number of parallel streaming sessions the bridge supports
    max_streams: int | None = 1
    # segments: Holds all parameters concerning the segmentations capabilities of a device
    segments: SegmentationProperties | None = None

    id_v1: str | None = None
    type: ResourceTypes = ResourceTypes.ENTERTAINMENT

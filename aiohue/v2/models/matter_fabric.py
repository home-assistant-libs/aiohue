"""
Model(s) for matter_fabric resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_matter_fabric
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from .resource import ResourceTypes


class MatterFabricStatus(Enum):
    """Enum with the possible MatterFabric statuses."""

    PENDING = "pending"
    PAIRED = "paired"
    TIMEDOUT = "timedout"


@dataclass
class MatterFabricData:
    """Human readable context to identify Matter fabric."""

    label: str
    vendor_id: int


@dataclass
class MatterFabric:
    """
    Represent a (full) `MatterFabric` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_matter_fabric_get
    """

    id: str
    status: MatterFabricStatus
    # NOTE: Only a fabric with status paired has fabric_data
    fabric_data: Optional[MatterFabricData] = None
    creation_time: Optional[datetime] = None
    id_v1: Optional[str] = None
    type: ResourceTypes = ResourceTypes.MATTER_FABRIC

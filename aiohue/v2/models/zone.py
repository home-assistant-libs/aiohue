"""Model(s) for Zone resource on HUE bridge."""
from dataclasses import dataclass
from types import NoneType
from typing import Optional

from .group import Group
from .resource import ResourceTypes
from .room import RoomMetadata


@dataclass
class Zone(Group):
    """
    Represent Zone object as received from the api.

    A group grouping only services.
    A service can be in an arbitrary amount of groups.
    Following services are allowed:
        - light - relative_rotary - temperature - lightlevel - motion

    clip-api.schema.json#/definitions/Zone
    """

    metadata: Optional[RoomMetadata] = None
    type: ResourceTypes = ResourceTypes.ZONE

    def __post_init__(self) -> None:
        """Make sure that data has valid type (allows creating from dict)."""
        super().__post_init__()
        if not isinstance(self.metadata, (NoneType, RoomMetadata)):
            self.metadata = RoomMetadata(**self.metadata)

    @property
    def grouped_light(self) -> str | None:
        """Return the grouped light id that is connected to this zone (if any)."""
        if not self.grouped_services:
            return None
        return next(
            (
                x.rid
                for x in self.grouped_services
                if x.rtype == ResourceTypes.GROUPED_LIGHT
            ),
            None,
        )

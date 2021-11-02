"""Model(s) for Zone resource on HUE bridge."""
from dataclasses import dataclass


from typing import Optional

from .group import Group
from .resource import ResourceTypes
from .room import RoomMetadata


@dataclass
class Zone(Group):
    """
    Represent Zone object as used by the Hue api.

    A group grouping only services.
    A service can be in an arbitrary amount of groups.
    Following services are allowed:
        - light - relative_rotary - temperature - lightlevel - motion

    clip-api.schema.json#/definitions/Zone
    """

    metadata: Optional[RoomMetadata] = None
    type: ResourceTypes = ResourceTypes.ZONE

    @property
    def grouped_light(self) -> Optional[str]:
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

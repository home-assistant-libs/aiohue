"""Controller/model for Hue resource of type Group."""

from __future__ import annotations

from collections.abc import Coroutine
from logging import Logger
from typing import Any, TypedDict

from .api import APIItems


class Groups(APIItems):
    """
    Represents Hue Groups (zone/room).

    https://developers.meethue.com/documentation/groups-api
    """

    def __init__(self, logger: Logger, raw: dict[str, Any], request: Coroutine) -> None:
        """Initialize instance."""
        super().__init__(logger, raw, request, "groups", Group)

    async def get_all_lights_group(self) -> Group:
        """Return special all lights group."""
        return Group("0", await self._request("get", "groups/0"), self._request)


class GroupState(TypedDict):
    """Represents state dict for a group."""

    all_on: bool
    any_on: bool


class GroupAction(TypedDict, total=False):
    """Represents action dict for a group."""

    on: bool
    bri: int  # optional
    hue: int  # optional
    sat: int  # optional
    effect: str  # optional
    xy: list[float]  # optional
    ct: int  # optional
    alert: str
    colormode: str  # optional


class Group:
    """Represents a Hue Group."""

    ITEM_TYPE = "groups"

    def __init__(self, id: str, raw: dict[str, Any], request: Coroutine) -> None:
        """Initialize instance."""
        self.id = id
        self.raw = raw
        self._request = request

    @property
    def type(self) -> str:
        """Return type of the group (Zone or Room)."""
        return self.raw["type"]

    @property
    def name(self) -> str:
        """Return name."""
        return self.raw["name"]

    @property
    def uniqueid(self) -> str:
        """
        Return Unique ID for the group.

        Requires API version 1.9+ and only for groups that are the type
        Luminaire or Lightsource.
        """
        return self.raw.get("uniqueid")

    @property
    def action(self) -> GroupAction:
        """Return current group action."""
        return GroupAction(self.raw["action"])

    @property
    def state(self) -> GroupState:
        """Return current group state."""
        return GroupState(self.raw["state"])

    @property
    def lights(self) -> list[str]:
        """Return id's of lights that are members of this group."""
        return self.raw["lights"]

    @property
    def sensors(self) -> list[str]:
        """Return id's of sensors that are members of this group."""
        return self.raw["sensors"]

    async def set_action(
        self,
        on=None,
        bri=None,
        hue=None,
        sat=None,
        xy=None,
        ct=None,
        alert=None,
        effect=None,
        transitiontime=None,
        bri_inc=None,
        sat_inc=None,
        hue_inc=None,
        ct_inc=None,
        xy_inc=None,
        scene=None,
    ) -> None:
        """Change action of a group."""
        data = {
            key: value
            for key, value in {
                "on": on,
                "bri": bri,
                "hue": hue,
                "sat": sat,
                "xy": xy,
                "ct": ct,
                "alert": alert,
                "effect": effect,
                "transitiontime": transitiontime,
                "bri_inc": bri_inc,
                "sat_inc": sat_inc,
                "hue_inc": hue_inc,
                "ct_inc": ct_inc,
                "xy_inc": xy_inc,
                "scene": scene,
            }.items()
            if value is not None
        }

        await self._request("put", f"groups/{self.id}/action", json=data)

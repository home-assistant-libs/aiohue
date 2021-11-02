from __future__ import annotations
from collections import namedtuple
from logging import Logger
from typing import Any, Coroutine, Dict

from .api import APIItems

# Represents a CIE 1931 XY coordinate pair.
XYPoint = namedtuple("XYPoint", ["x", "y"])


# Represents the Gamut of a light.
GamutType = namedtuple("GamutType", ["red", "green", "blue"])


class Lights(APIItems):
    """
    Represents Hue Lights.

    https://developers.meethue.com/documentation/lights-api
    """

    def __init__(self, logger: Logger, raw: Dict[str, Any], request: Coroutine) -> None:
        """Initialize instance."""
        super().__init__(logger, raw, request, "lights", Light)


class Light:
    """Represents a Hue light."""

    ITEM_TYPE = "lights"

    def __init__(self, id: str, raw: Dict[str, Any], request: Coroutine) -> None:
        """Initialize instance."""
        self.id = id
        self.raw = raw
        self._request = request

    @property
    def uniqueid(self):
        return self.raw["uniqueid"]

    @property
    def manufacturername(self):
        return self.raw["manufacturername"]

    @property
    def modelid(self):
        return self.raw["modelid"]

    @property
    def productname(self):
        # productname added in Bridge API 1.24 (published 03/05/2018)
        return self.raw.get("productname")

    @property
    def name(self):
        return self.raw["name"]

    @property
    def state(self):
        return self.raw["state"]

    @property
    def type(self):
        return self.raw["type"]

    @property
    def swversion(self):
        """Software version of the light."""
        return self.raw["swversion"]

    @property
    def swupdatestate(self):
        """Software update state of the light."""
        return self.raw.get("swupdate", {}).get("state")

    @property
    def controlcapabilities(self):
        """Capabilities that the light has to control it."""
        return self.raw.get("capabilities", {}).get("control", {})

    @property
    def colorgamuttype(self):
        """The color gamut type of the light."""
        light_spec = self.controlcapabilities
        return light_spec.get("colorgamuttype", "None")

    @property
    def colorgamut(self):
        """The color gamut information of the light."""
        try:
            light_spec = self.controlcapabilities
            gtup = tuple([XYPoint(*x) for x in light_spec["colorgamut"]])
            color_gamut = GamutType(*gtup)
        except KeyError:
            color_gamut = None

        return color_gamut

    async def set_state(
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
    ):
        """Change state of a light."""
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
            }.items()
            if value is not None
        }

        await self._request("put", "lights/{}/state".format(self.id), json=data)

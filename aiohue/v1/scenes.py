from __future__ import annotations
from .api import APIItems


class Scenes(APIItems):
    """Represents Hue Scenes.

    https://developers.meethue.com/documentation/scenes-api
    """

    def __init__(self, logger, raw, request):
        super().__init__(logger, raw, request, "scenes", Scene)


class Scene:
    """Represents a Hue Scene."""

    ITEM_TYPE = "scenes"

    def __init__(self, id, raw, request):
        self.id = id
        self.raw = raw
        self._request = request

    @property
    def name(self):
        return self.raw["name"]

    @property
    def lights(self):
        return self.raw["lights"]

    @property
    def owner(self):
        return self.raw["owner"]

    @property
    def recycle(self):
        return self.raw["recycle"]

    @property
    def locked(self):
        return self.raw["locked"]

    @property
    def appdata(self):
        return self.raw["appdata"]

    @property
    def picture(self):
        return self.raw["picture"]

    @property
    def lastupdated(self):
        return self.raw["lastupdated"]

    @property
    def version(self):
        return self.raw["version"]

    @property
    def lightstates(self):
        return self.get_lightstates()

    async def get_lightstates(self):
        data = await self._request("get", "scenes/{}".format(self.id))
        return data["lightstates"]

    async def set_lightstate(
        self,
        id=None,
        on=None,
        bri=None,
        hue=None,
        sat=None,
        xy=None,
        ct=None,
    ):
        """Change state of a light in scene."""
        data = {}
        data['name'] = self.name
        data['lightstates'] = {}
        if id is not None:
            data['lightstates'][id] = {
                key: value
                for key, value in {
                    "on": on,
                    "bri": bri,
                    "hue": hue,
                    "sat": sat,
                    "xy": xy,
                    "ct": ct,
                }.items()
                if value is not None
            }
        await self._request("put", "scenes/{}".format(self.id), json=data)

from .api import APIItems


class Scenes(APIItems):
    """Represents Hue Scenes.

    https://developers.meethue.com/documentation/scenes-api
    """

    def __init__(self, raw, request):
        super().__init__(raw, request, "scenes", Scene)


class Scene:
    """Represents a Hue Scene."""

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

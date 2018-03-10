from .api import APIItems


class Scenes(APIItems):
    """Represents Hue Scenes.

    https://developers.meethue.com/documentation/scenes-api
    """

    def __init__(self, raw, request):
        super().__init__(raw, request, 'scenes', Scene)


class Scene:
    """Represents a Hue Scene."""
    def __init__(self, id, raw, request):
        self.id = id
        self.raw = raw
        self._request = request

    @property
    def name(self):
        return self.raw['name']

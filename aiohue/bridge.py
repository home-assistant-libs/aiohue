from aiohttp.client_exceptions import ClientError

from .config import Config
from .groups import Groups
from .lights import Lights
from .scenes import Scenes
from .sensors import Sensors
from .errors import raise_error


class Bridge:
    """Control a Hue bridge."""

    def __init__(self, host, websession, *, username=None, bridge_id=None):
        self.host = host
        self.username = username
        self.websession = websession
        self._bridge_id = bridge_id

        self.proto = None
        self.config = None
        self.groups = None
        self.lights = None
        self.scenes = None
        self.sensors = None

        # self.capabilities = None
        # self.rules = None
        # self.schedules = None

    @property
    def id(self):
        """Return the ID of the bridge."""
        if self.config is not None:
            return self.config.bridgeid

        return self._bridge_id

    async def _figure_out_protocol(self):
        """Figure out the Hue protocol.

        Hue switched to `https` communications, to remain backward compatible,
        we try to see if `https` works first. If not, we fallback to `http`.
        """
        if self.proto is not None:
            return

        self.proto = "https"

        try:
            await self.request("head", "")
        except ClientError:
            self.proto = "http"

    async def create_user(self, device_type):
        """Create a user.

        https://developers.meethue.com/documentation/configuration-api#71_create_user
        """
        await self._figure_out_protocol()
        result = await self.request("post", "", {"devicetype": device_type}, auth=False)
        self.username = result[0]["success"]["username"]
        return self.username

    async def initialize(self):
        await self._figure_out_protocol()
        result = await self.request("get", "")

        self.config = Config(result["config"], self.request)
        self.groups = Groups(result["groups"], self.request)
        self.lights = Lights(result["lights"], self.request)
        if "scenes" in result:
            self.scenes = Scenes(result["scenes"], self.request)
        if "sensors" in result:
            self.sensors = Sensors(result["sensors"], self.request)

    async def request(self, method, path, json=None, auth=True):
        """Make a request to the API."""
        url = "{}://{}/api/".format(self.proto, self.host)
        if auth:
            url += "{}/".format(self.username)
        url += path

        async with self.websession.request(method, url, json=json, ssl=False) as res:
            res.raise_for_status()
            data = await res.json()
            _raise_on_error(data)
            return data


def _raise_on_error(data):
    """Check response for error message."""
    if isinstance(data, list):
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_error(data["error"])

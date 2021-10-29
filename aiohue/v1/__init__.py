"""AIOHue implementation for HueBridge over V1/legacy api."""
import logging

import aiohttp

from .config import Config
from .groups import Groups
from .lights import Lights
from .scenes import Scenes
from .sensors import Sensors
from ..errors import raise_from_error

_DEFAULT = object()


class HueBridgeV1:
    """Control a Hue bridge with legacy/V1 API.."""

    def __init__(
        self,
        host: str,
        websession: aiohttp.ClientSession,
        *,
        username: str | None = None,
        bridge_id: str | None = None,
    ):
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

        self.logger = logging.getLogger(f"{__name__}.{host}")

    @property
    def id(self):
        """Return the ID of the bridge."""
        if self.config is not None:
            return self.config.bridgeid

        return self._bridge_id

    async def create_user(self, device_type):
        """Create a user.

        https://developers.meethue.com/documentation/configuration-api#71_create_user
        """
        result = await self.request("post", "", {"devicetype": device_type}, auth=False)
        self.username = result[0]["success"]["username"]
        return self.username

    async def initialize(self):
        """Initialize state by fetching all items once."""
        result = await self.request("get", "")
        self.config = Config(result.pop("config"), self.request)

        self.groups = Groups(self.logger, result.pop("groups"), self.request)
        self.lights = Lights(self.logger, result.pop("lights"), self.request)
        if "scenes" in result:
            self.scenes = Scenes(self.logger, result.pop("scenes"), self.request)
        if "sensors" in result:
            self.sensors = Sensors(self.logger, result.pop("sensors"), self.request)

        self.logger.debug("Unused result: %s", result)

    async def request(self, method, path, json=None, auth=True):
        """Make a request to the API."""
        # Old bridges and incompatible emulates still use `http`
        # so we only use http
        url = f"http://{self.host}/api/"
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
        raise_from_error(data["error"])

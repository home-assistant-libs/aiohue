"""AIOHue implementation for HueBridge over V1/legacy api."""
import logging
from types import TracebackType
from typing import Optional, Type

import aiohttp
from asyncio_throttle import Throttler

from ..errors import Unauthorized, raise_from_error
from .config import Config
from .groups import Groups
from .lights import Lights
from .scenes import Scenes
from .sensors import Sensors


class HueBridgeV1:
    """Control a Hue bridge with legacy/V1 API.."""

    def __init__(
        self,
        host: str,
        websession: aiohttp.ClientSession | None = None,
        app_key: str | None = None,
    ) -> None:
        """
        Initialize the Bridge instance.

        Parameters:
            `host`: the hostname or IP-address of the bridge as string.
            `websession`: optionally provide a aiohttp ClientSession.
            `app_key`: optionally provide a hue appkey/username for authentication.

            NOTE: You'll need to call initialize before any data is available.
            NOTE: If app_key is not provided, you need to call create_user.
        """
        self._host = host
        self._app_key = app_key
        self._websession = websession
        self._websession_provided = websession is not None

        self.logger = logging.getLogger(f"{__package__}[{host}]")
        self._throttler = Throttler(rate_limit=3, period=1)
        # all api controllers
        self._config = None
        self._devices = None
        self._lights = None
        self._scenes = None
        self._groups = None
        self._sensors = None

    @property
    def bridge_id(self) -> str | None:
        """Return the ID of the bridge we're currently connected to."""
        return self._config.bridge_id if self._config else None

    @property
    def host(self) -> str:
        """Return the hostname of the bridge."""
        return self._host

    @property
    def config(self) -> Config | None:
        """Get the bridge config."""
        return self._config

    @property
    def lights(self) -> Lights | None:
        """Get the light resources."""
        return self._lights

    @property
    def scenes(self) -> Scenes | None:
        """Get the scene resources."""
        return self._scenes

    @property
    def groups(self) -> Groups | None:
        """Get the group resources."""
        return self._groups

    @property
    def sensors(self) -> Sensors | None:
        """Get the sensor resources."""
        return self._sensors

    async def create_user(self, device_type: str) -> str:
        """
        Create a user and return it's app_key for authentication.

        https://developers.meethue.com/documentation/configuration-api#71_create_user
        """
        result = await self.request("post", "", {"devicetype": device_type}, auth=False)
        self._app_key = result[0]["success"]["username"]
        return self._app_key

    async def initialize(self):
        """Initialize the connection to the bridge and fetch all data."""
        if self._app_key is None:
            raise Unauthorized("There is no app_key provided or requested.")

        result = await self.request("get", "")
        self._config = Config(result.pop("config"), self.request)
        self._groups = Groups(self.logger, result.pop("groups"), self.request)
        self._lights = Lights(self.logger, result.pop("lights"), self.request)
        if "scenes" in result:
            self._scenes = Scenes(self.logger, result.pop("scenes"), self.request)
        if "sensors" in result:
            self._sensors = Sensors(self.logger, result.pop("sensors"), self.request)

        self.logger.debug("Unused result: %s", result)

    async def close(self) -> None:
        """Close connection and cleanup."""
        if not self._websession_provided:
            await self._websession.close()
        self.logger.info("Connection to bridge closed.")

    async def request(self, method, path, json=None, auth=True):
        """Make a request to the API."""

        if self._websession is None:
            self._websession = aiohttp.ClientSession()

        # Old bridges and most emulators only use `http`
        url = f"http://{self.host}/api/"
        if auth:
            url += "{}/".format(self._app_key)
        url += path

        async with self._websession.request(method, url, json=json) as res:
            res.raise_for_status()
            data = await res.json()
            _raise_on_error(data)
            return data

    async def __aenter__(self) -> "HueBridgeV1":
        """Return Context manager."""
        if self._app_key:
            await self.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> Optional[bool]:
        """Exit context manager."""
        await self.close()
        if exc_val:
            raise exc_val
        return exc_type


def _raise_on_error(data):
    """Check response for error message."""
    if isinstance(data, list):
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_from_error(data["error"])
"""AIOHue implementation for HueBridge over V1/legacy api."""
from __future__ import annotations
import logging
from types import TracebackType
from typing import Optional, Type

import aiohttp

from ..errors import raise_from_error
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
        app_key: str,
        websession: aiohttp.ClientSession | None = None,
    ) -> None:
        """
        Initialize the Bridge instance.

        Parameters:
            `host`: the hostname or IP-address of the bridge as string.
            `app_key`: provide the hue appkey/username for authentication.
            `websession`: optionally provide a aiohttp ClientSession.
        """
        self._host = host
        self._app_key = app_key
        self._websession = websession
        self._websession_provided = websession is not None

        self.logger = logging.getLogger(f"{__package__}[{host}]")
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

    async def initialize(self):
        """Initialize the connection to the bridge and fetch all data."""
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

    async def request(self, method, endpoint, json=None):
        """Make a request to the API."""
        if self._websession is None:
            self._websession = aiohttp.ClientSession()

        # Old bridges and (most) emulators only use `http`
        url = f"http://{self.host}/api/{self._app_key}/{endpoint}"

        async with self._websession.request(method, url, json=json) as res:
            res.raise_for_status()
            data = await res.json()
            _raise_on_error(data)
            return data

    async def __aenter__(self) -> "HueBridgeV1":
        """Return Context manager."""
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

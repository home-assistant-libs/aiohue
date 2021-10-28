"""Control a Philips Hue bridge with V2 API."""

import asyncio
from contextlib import asynccontextmanager
import logging
from types import TracebackType
from typing import Generator, List, Optional, Type

import aiohttp
from aiohttp import ClientResponse
from asyncio_throttle import Throttler

from .errors import raise_from_error
from .controllers.events import EventStream

from .controllers.bridge_config import BridgeConfigController
from .controllers.sensors import SensorsController
from .controllers.lights import LightsController
from .controllers.groups import GroupsController
from .controllers.scenes import ScenesController
from .controllers.devices import DevicesController


class HueBridgeV2:
    """Control a Philips Hue bridge with V2 API."""

    def __init__(
        self,
        host: str,
        app_key: str | None = None,
        websession: aiohttp.ClientSession | None = None,
    ) -> None:
        """
        Initialize the Bridge instance.

            host: the hostname or IP-address of the bridge as string.
            websession: optionally provide a aiohttp ClientSession.
            app_key: optionally provide a hue appkey/username for authentication.

            NOTE: You'll need to call initialize before any data is available.
        """
        self._host = host
        self._app_key = app_key
        self._websession = websession
        self._websession_provided = websession is not None

        self.logger = logging.getLogger(f"{__package__}[{host}]")
        self._throttler = Throttler(rate_limit=10, period=1)
        self._events = EventStream(self)
        # all resource controllers
        self._bridge_config = BridgeConfigController(self)
        self._devices = DevicesController(self)
        self._lights = LightsController(self)
        self._scenes = ScenesController(self)
        self._groups = GroupsController(self)
        self._sensors = SensorsController(self)

    @property
    def bridge_id(self) -> str | None:
        """Return the ID of the bridge we're currently connected to."""
        return self._resources.bridge_config.id

    @property
    def host(self) -> str:
        """Return the hostname of the bridge."""
        return self._host

    @property
    def events(self) -> EventStream:
        """Return the EventStream controller."""
        return self._events

    @property
    def bridge_config(self) -> BridgeConfigController:
        """Get the Bridge(config) Controller."""
        return self._bridge_config

    @property
    def devices(self) -> DevicesController:
        """Get the Devices Controller for managing all device resources."""
        return self._devices

    @property
    def lights(self) -> LightsController:
        """Get the Lights Controller for managing all light resources."""
        return self._lights

    @property
    def scenes(self) -> ScenesController:
        """Get the Scenes Controller for managing all scene resources."""
        return self._scenes

    @property
    def groups(self) -> GroupsController:
        """Get the Groups Controller for managing all group resources."""
        return self._groups

    @property
    def sensors(self) -> SensorsController:
        """Get the Sensors Controller for managing all sensor resources."""
        return self._sensors

    async def create_user(self, device_type: str) -> str:
        """
        Create a user and return it's app_key for authentication.

        https://developers.meethue.com/documentation/configuration-api#71_create_user
        """
        result = await self.request(
            "post", "", legacy=True, auth=False, json={"devicetype": device_type}
        )
        self._app_key = result[0]["success"]["username"]
        return self._app_key

    async def __aenter__(self) -> "HueBridgeV2":
        """Return Context manager."""
        assert self._app_key is not None
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
        return exc_val

    async def initialize(self) -> None:
        """Initialize the connection to the bridge and fetch all data."""
        if self._websession is None:
            self._websession = aiohttp.ClientSession()

        # Initialize all HUE resource controllers
        # fetch complete full state once and distribute to controllers
        full_state = await self.request("get", "clip/v2/resource")

        await asyncio.gather(
            self._bridge_config.initialize(full_state),
            self._devices.initialize(full_state),
            self._lights.initialize(full_state),
            self._scenes.initialize(full_state),
            self._sensors.initialize(full_state),
            self._groups.initialize(full_state),
        )
        # start event listener
        await self._events.initialize()

    async def close(self) -> None:
        """Close connection and cleanup."""
        await self.events.stop()
        if not self._websession_provided:
            await self._websession.close()
        self.logger.info("Connection to bridge closed.")

    async def request(self, method: str, path: str, **kwargs) -> dict | List[dict]:
        """Make request on the api and return response data."""
        async with self.create_request(method, path, **kwargs) as resp:
            result = await resp.json()
            if result.get("errors"):
                raise_from_error(result["errors"][0])
            return result["data"]

    @asynccontextmanager
    async def create_request(
        self, method: str, path: str, **kwargs
    ) -> Generator[ClientResponse, None, None]:
        """
        Make a request to any path with V2 request method (auth in header).

        Takes rate limiting (throttling) into account for connections.
        Returns a generator with aiohttp ClientResponse.
        """
        url = f"https://{self._host}/{path}"

        kwargs["ssl"] = False

        if "headers" not in kwargs:
            kwargs["headers"] = {}

        if self._app_key is not None:
            kwargs["headers"]["hue-application-key"] = self._app_key

        async with self._throttler:
            async with self._websession.request(method, url, **kwargs) as res:
                res.raise_for_status()
                yield res

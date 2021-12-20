"""Control a Philips Hue bridge with V2 API."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import logging
from types import TracebackType
from typing import Callable, Generator, List, Optional, Type

import aiohttp
from aiohttp import ClientResponse

from aiohue.v2.models.clip import CLIPResource

from ..errors import Unauthorized, raise_from_error
from .controllers.events import EventCallBackType, EventStream, EventType

from .controllers.config import ConfigController
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
        self._events = EventStream(self)
        # all resource controllers
        self._config = ConfigController(self)
        self._devices = DevicesController(self)
        self._lights = LightsController(self)
        self._scenes = ScenesController(self)
        self._groups = GroupsController(self)
        self._sensors = SensorsController(self)

    @property
    def bridge_id(self) -> str | None:
        """Return the ID of the bridge we're currently connected to."""
        return self._config.bridge_id

    @property
    def host(self) -> str:
        """Return the hostname of the bridge."""
        return self._host

    @property
    def events(self) -> EventStream:
        """Return the EventStream controller."""
        return self._events

    @property
    def config(self) -> ConfigController:
        """Get the Config Controller with config-like resources."""
        return self._config

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

    async def initialize(self) -> None:
        """Initialize the connection to the bridge and fetch all data."""
        # Initialize all HUE resource controllers
        # fetch complete full state once and distribute to controllers
        await self.fetch_full_state()
        # start event listener
        await self._events.initialize()
        # subscribe to reconnect event
        self._events.subscribe(self._handle_event, EventType.RECONNECTED)

    async def close(self) -> None:
        """Close connection and cleanup."""
        await self.events.stop()
        if not self._websession_provided:
            await self._websession.close()
        self.logger.info("Connection to bridge closed.")

    def subscribe(
        self,
        callback: EventCallBackType,
    ) -> Callable:
        """
        Subscribe to status changes for all resources.

        Returns:
            function to unsubscribe.
        """
        unsubscribes = [
            self.config.subscribe(callback),
            self.devices.subscribe(callback),
            self.groups.subscribe(callback),
            self.lights.subscribe(callback),
            self.scenes.subscribe(callback),
            self.sensors.subscribe(callback),
        ]

        def unsubscribe():
            for unsub in unsubscribes:
                unsub()

        return unsubscribe

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

        Returns a generator with aiohttp ClientResponse.
        """
        if self._websession is None:
            self._websession = aiohttp.ClientSession()

        url = f"https://{self._host}/{path}"

        kwargs["ssl"] = False

        if "headers" not in kwargs:
            kwargs["headers"] = {}

        kwargs["headers"]["hue-application-key"] = self._app_key

        retries = 0
        while retries <= 25:
            async with self._websession.request(method, url, **kwargs) as res:
                if res.status == 403:
                    raise Unauthorized
                if res.status == 503:
                    # 503 means the bridge is rate limiting, we should back off a bit.
                    retries += 1
                    await asyncio.sleep(0.5 * retries)
                    continue
                res.raise_for_status()
                yield res
                break

    async def __aenter__(self) -> "HueBridgeV2":
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

    async def _handle_event(self, type: EventType, item: CLIPResource | None) -> None:
        """Handle incoming event for this resource from the EventStream."""
        if type != EventType.RECONNECTED:
            return
        await self.fetch_full_state()

    async def fetch_full_state(self) -> None:
        """Fetch state on all controllers."""
        full_state = await self.request("get", "clip/v2/resource")
        await asyncio.gather(
            self._config.initialize(full_state),
            self._devices.initialize(full_state),
            self._lights.initialize(full_state),
            self._scenes.initialize(full_state),
            self._sensors.initialize(full_state),
            self._groups.initialize(full_state),
        )

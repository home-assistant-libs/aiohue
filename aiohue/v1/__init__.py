"""AIOHue implementation for HueBridge over V1/legacy api."""

from __future__ import annotations

import asyncio
import logging
from types import TracebackType

import aiohttp
from asyncio_throttle import Throttler

from aiohue.errors import BridgeBusy, Unauthorized, raise_from_error

from .config import Config
from .groups import Groups
from .lights import Lights
from .scenes import Scenes
from .sensors import Sensors

# how many times do we retry on a 503 or 429 (bridge overload/rate limit)
MAX_RETRIES = 25
THROTTLE_CONCURRENT_REQUESTS = 1  # how many concurrent requests to the bridge
THROTTLE_TIMESPAN = 0.25  # timespan/period (in seconds) for the rate limiting


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
        # Setup the Throttler/rate limiter for requests to the bridge.
        self._throttler = Throttler(
            rate_limit=THROTTLE_CONCURRENT_REQUESTS, period=THROTTLE_TIMESPAN
        )

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
        """Make request on the api and return response data."""
        if self._websession is None:
            self._websession = aiohttp.ClientSession()

        # Old bridges and (most) emulators only use `http`
        url = f"http://{self.host}/api/{self._app_key}/{endpoint}"
        # The bridge will rate limit if we send more requests than about 2-5 per second
        # we guard ourselves from hitting the rate limit by using a throttler
        # but others apps/services are hitting the Hue bridge too so we still
        # might hit the rate limit/overload at some point so we also retry if this happens.
        retries = 0

        while retries < MAX_RETRIES:
            retries += 1

            if retries > 1:
                retry_wait = 0.25 * retries
                self.logger.debug(
                    "Got 503 or 429 error from Hue bridge, retry request in %s seconds",
                    retry_wait,
                )
                await asyncio.sleep(retry_wait)

            async with self._websession.request(method, url, json=json) as resp:
                # 503 means the service is temporarily unavailable, back off a bit.
                if resp.status == 503:
                    continue
                # 429 means the bridge is rate limiting/overloaded, we should back off a bit.
                if resp.status == 429:
                    continue
                if resp.status == 403:
                    raise Unauthorized
                # raise on all other error status codes
                resp.raise_for_status()
                data = await resp.json()
                _raise_on_error(data)
                return data

        raise BridgeBusy(
            f"{retries} requests to the bridge failed, "
            "its probably overloaded. Giving up."
        )

    async def __aenter__(self) -> HueBridgeV1:
        """Return Context manager."""
        await self.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> bool | None:
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

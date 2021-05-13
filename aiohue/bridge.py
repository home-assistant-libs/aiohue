from __future__ import annotations
import asyncio

import logging

import aiohttp
from aiohttp.client_exceptions import ClientConnectionError

from .config import Config
from .clip import Clip
from .groups import Groups
from .lights import Lights
from .scenes import Scenes
from .sensors import Sensors
from .errors import raise_error


class Bridge:
    """Control a Hue bridge."""

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
        self.clip = Clip(self.request_2)

        self.logger = logging.getLogger(f"{__name__}.{host}")

        # self.capabilities = None
        # self.rules = None
        # self.schedules = None

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
        result = await self.request("get", "")

        self.config = Config(result.pop("config"), self.request)
        self.groups = Groups(result.pop("groups"), self.request)
        self.lights = Lights(result.pop("lights"), self.request)
        if "scenes" in result:
            self.scenes = Scenes(result.pop("scenes"), self.request)
        if "sensors" in result:
            self.sensors = Sensors(result.pop("sensors"), self.request)

        logging.getLogger(__name__).debug("Unused result: %s", result)

    async def request(self, method, path, json=None, auth=True):
        """Make a request to the API."""
        # By default we assume we need to connect over `https`
        # Old bridges and incompatible emulates still use `http` so we force a fallback
        # We will store protocol in `self.proto` if request succesful.
        if self.proto is None:
            proto = "https"
        else:
            proto = self.proto

        url = "{}://{}/api/".format(proto, self.host)
        if auth:
            url += "{}/".format(self.username)
        url += path

        try:
            async with self.websession.request(
                method, url, json=json, ssl=False
            ) as res:
                res.raise_for_status()

                # Store the protocol that worked
                if self.proto is None:
                    self.proto = proto

                data = await res.json()
                _raise_on_error(data)
                return data

        except ClientConnectionError:
            if self.proto is not None:
                raise

            self.proto = "http"
            return await self.request(method, path, json, auth)

    async def request_2(self, method, path):
        """Make a request to any path with Hue's new request method.

        This method has the auth in a header.
        """
        url = f"{self.proto}://{self.host}/{path}"

        async with self.websession.request(
            method, url, ssl=False, headers={"hue-application-key": self.username}
        ) as res:
            res.raise_for_status()
            return await res.json()

    async def listen_events(self):
        """Listen to events and apply changes to objects."""
        loop = asyncio.get_running_loop()
        pending_events = asyncio.Queue()

        async def receive_events():
            while True:
                for event in await self.clip.next_events():
                    pending_events.put_nowait(event)

        event_task = loop.create_task(receive_events())
        try:
            while True:
                event = await pending_events.get()

                if event["type"] != "update":
                    self.logger.debug("Unknown event: %s", event)
                    continue

                for update in event["data"]:
                    item_type = update["id_v1"].split("/", 2)[1]

                    if item_type == "lights":
                        obj = self.lights.process_update_event(update)
                        # if obj is None, we didn't know the object
                        # We could consider triggering a full refresh
                        if obj is not None:
                            yield obj

        except asyncio.CancelledError:
            event_task.cancel()
            raise


def _raise_on_error(data):
    """Check response for error message."""
    if isinstance(data, list):
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_error(data["error"])

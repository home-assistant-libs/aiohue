from __future__ import annotations

import asyncio
import logging

import aiohttp
from aiohttp import client_exceptions

from .clip import Clip
from .config import Config
from .errors import raise_error
from .groups import Groups
from .lights import Lights
from .scenes import Scenes
from .sensors import Sensors

_DEFAULT = object()


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
        self.groups = Groups(self.logger, result.pop("groups"), self.request)
        self.lights = Lights(self.logger, result.pop("lights"), self.request)
        if "scenes" in result:
            self.scenes = Scenes(self.logger, result.pop("scenes"), self.request)
        if "sensors" in result:
            self.sensors = Sensors(self.logger, result.pop("sensors"), self.request)

        self.logger.debug("Unused result: %s", result)

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

        except client_exceptions.ClientConnectionError:
            if self.proto is not None:
                raise

            self.proto = "http"
            return await self.request(method, path, json, auth)

    async def request_2(self, method, path, timeout=_DEFAULT):
        """Make a request to any path with Hue's new request method.

        This method has the auth in a header.
        """
        url = f"{self.proto or 'https'}://{self.host}/{path}"

        kwargs = {
            "ssl": False,
            "headers": {"hue-application-key": self.username},
        }

        if timeout is not _DEFAULT:
            kwargs["timeout"] = timeout

        async with self.websession.request(method, url, **kwargs) as res:
            res.raise_for_status()
            return await res.json()

    async def listen_events(self):
        """Listen to events and apply changes to objects."""
        pending_events = asyncio.Queue()

        async def receive_events():
            while True:
                self.logger.debug("Subscribing to events")
                try:
                    for event in await self.clip.next_events():
                        self.logger.debug("Received event: %s", event)
                        pending_events.put_nowait(event)
                except client_exceptions.ServerDisconnectedError:
                    self.logger.debug("Event endpoint disconnected")
                except client_exceptions.ClientError as err:
                    if isinstance(err, client_exceptions.ClientResponseError):
                        # We get 503 when it's too busy, but any other error
                        # is probably also because too busy.
                        self.logger.debug(
                            "Got status %s from endpoint. Sleeping while waiting to resolve",
                            err.status,
                        )
                    else:
                        self.logger.debug("Unable to reach event endpoint: %s", err)

                    await asyncio.sleep(5)
                except asyncio.TimeoutError:
                    pass
                except Exception:
                    self.logger.exception("Unexpected error")
                    pending_events.put(None)
                    break

        event_task = asyncio.create_task(receive_events())

        while True:
            try:
                event = await pending_events.get()
            except asyncio.CancelledError:
                event_task.cancel()
                await event_task
                raise

            # If unexpected error occurred
            if event is None:
                return

            if event["type"] not in ("update", "motion"):
                self.logger.debug("Unknown event type: %s", event)
                continue

            for event_data in event["data"]:
                # We don't track object that groups all items (bridge_home)
                if event_data["id_v1"] == "/groups/0":
                    continue

                item_type = event_data["id_v1"].split("/", 2)[1]

                if item_type not in (
                    # These all inherit from APIItems and so can handle events
                    "lights",
                    "sensors",
                    "scenes",
                    "groups",
                ):
                    self.logger.debug(
                        "Received %s event for unknown item type %s: %s",
                        event["type"],
                        item_type,
                        event_data,
                    )
                    continue

                obj = getattr(self, item_type).process_event(event["type"], event_data)
                # if obj is None, we didn't know the object
                # We could consider triggering a full refresh
                if obj is not None:
                    yield obj


def _raise_on_error(data):
    """Check response for error message."""
    if isinstance(data, list):
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_error(data["error"])

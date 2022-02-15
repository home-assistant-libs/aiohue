"""Handle connecting to the HUE Eventstream and distribute events."""
from __future__ import annotations

import asyncio
import json
import random
import string
from asyncio.coroutines import iscoroutinefunction
from enum import Enum
from typing import TYPE_CHECKING, Callable, List, NoReturn, Tuple, TypedDict

from aiohttp import ClientTimeout
from aiohttp.client_exceptions import ClientError

from ...errors import AiohueException, InvalidAPIVersion, InvalidEvent, Unauthorized
from ...util import NoneType
from ..models.geofence_client import GeofenceClientPost, GeofenceClientPut
from ..models.resource import ResourceTypes

if TYPE_CHECKING:
    from .. import HueBridgeV2


CONNECTION_TIMEOUT = 90  # 90 seconds
KEEPALIVE_INTERVAL = 60  # every minute


class EventStreamStatus(Enum):
    """Status options of EventStream."""

    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2


class HueEvent(TypedDict):
    """Hue Event message as emitted by the EventStream."""

    id: str  # UUID
    creationtime: str
    type: str  # = EventType (add, update, delete)
    # data contains a list with (partial) resource objects
    # in case of add or update this is a full or partial resource object
    # in case of delete this will include only the
    # ResourceIndentifier (type and id) of the deleted object
    data: List[dict]


class EventType(Enum):
    """Enum with possible Events."""

    # resource events match those emitted by Hue eventstream
    RESOURCE_ADDED = "add"
    RESOURCE_UPDATED = "update"
    RESOURCE_DELETED = "delete"
    # connection events emitted by (this) events controller
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTED = "reconnected"


EventCallBackType = Callable[[EventType, dict | None], None]
EventSubscriptionType = Tuple[
    EventCallBackType,
    "Tuple[EventType] | None",
    "Tuple[ResourceTypes] | None",
]


class EventStream:
    """Holds the connection to the HUE Clip EventStream."""

    def __init__(self, bridge: "HueBridgeV2") -> None:
        """Initialize instance."""
        self._bridge = bridge
        self._listeners = set()
        self._event_queue = asyncio.Queue()
        self._last_event_id = ""
        self._status = EventStreamStatus.DISCONNECTED
        self._bg_tasks: List[asyncio.Task] = []
        self._subscribers: List[EventSubscriptionType] = []
        self._logger = bridge.logger.getChild("events")

    @property
    def connected(self) -> bool:
        """Return bool if we're connected."""
        return self._status == EventStreamStatus.CONNECTED

    @property
    def status(self) -> bool:
        """Return connection status."""
        return self._status

    async def initialize(self) -> None:
        """
        Start listening for events.

        Starts the connection to the Hue Eventstream and collect events.
        Connection will be auto-reconnected if it gets lost.
        """
        assert len(self._bg_tasks) == 0
        self._bg_tasks.append(asyncio.create_task(self.__event_reader()))
        self._bg_tasks.append(asyncio.create_task(self.__event_processor()))
        self._bg_tasks.append(asyncio.create_task(self.__keepalive_workaround()))

    async def stop(self) -> None:
        """Stop listening for events."""
        for task in self._bg_tasks:
            task.cancel()
        self._bg_tasks = []

    def subscribe(
        self,
        callback: EventCallBackType,
        event_filter: EventType | Tuple[EventType] | None = None,
        resource_filter: ResourceTypes | Tuple[ResourceTypes] | None = None,
    ) -> Callable:
        """
        Subscribe to events emitted by the Hue bridge for resources.

        Parameters:
            - `callback` - callback function to call when an event emits.
            - `event_filter` - Optionally provide an EventType as filter.
            - `resource_filter` - Optionally provide a ResourceType as filter.

        Returns:
            function to unsubscribe.
        """
        if not isinstance(event_filter, (NoneType, tuple)):
            event_filter = (event_filter,)
        if not isinstance(resource_filter, (NoneType, tuple)):
            resource_filter = (resource_filter,)
        subscription = (callback, event_filter, resource_filter)

        def unsubscribe():
            self._subscribers.remove(subscription)

        self._subscribers.append(subscription)
        return unsubscribe

    def emit(self, type: EventType, data: dict | None = None) -> None:
        """Emit event to all listeners."""
        for (callback, event_filter, resource_filter) in self._subscribers:
            if event_filter is not None and type not in event_filter:
                continue
            if (
                data is not None
                and resource_filter is not None
                and ResourceTypes(data.get("type")) not in resource_filter
            ):
                continue
            if iscoroutinefunction(callback):
                asyncio.create_task(callback(type, data))
            else:
                callback(type, data)

    async def __event_reader(self) -> NoReturn:
        """

        Read incoming SSE messages and put them in a Queue to be processed.

        Background task that keeps (re)connecting untill stopped.

        https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation
        """
        self._status = EventStreamStatus.CONNECTING
        connect_attempts = 0
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "close",
        }

        while True:
            connect_attempts += 1
            if self._last_event_id:
                headers["last-event-id"] = self._last_event_id
            # Messages come in line by line, according to EventStream/SSE specs
            # we iterate over the incoming lines in the streamreader.
            try:
                async with self._bridge.create_request(
                    "get",
                    "eventstream/clip/v2",
                    timeout=ClientTimeout(total=0, sock_read=CONNECTION_TIMEOUT),
                    headers=headers,
                ) as resp:
                    # update status to connected once we reach this point
                    self._status = EventStreamStatus.CONNECTED
                    if connect_attempts == 1:
                        self.emit(EventType.CONNECTED)
                    else:
                        self.emit(EventType.RECONNECTED)
                    connect_attempts = 1  # reset on succesfull connect
                    self._logger.debug("Connected to EventStream")
                    # read over incoming messages line by line
                    async for line in resp.content:
                        # process the message
                        self.__parse_message(line)
            except (ClientError, asyncio.TimeoutError) as err:
                # pass expected connection errors because we will auto retry
                status = getattr(err, "status", None)
                if status == 404:
                    raise InvalidAPIVersion from err
                if status == 403:
                    raise Unauthorized from err
                if status:
                    # for debugging purpose only
                    self._logger.debug(err)
            except Exception as err:
                # for debugging purpose only
                self._logger.exception(err)
                raise err

            # if we reach this point, the connection was lost
            self.emit(EventType.DISCONNECTED)

            reconnect_wait = min(2 * connect_attempts, 600)
            self._logger.debug(
                "Disconnected from EventStream"
                " - Reconnect will be attempted in %s seconds",
                reconnect_wait,
            )
            # every 10 failed connect attempts log warning
            if connect_attempts % 10 == 0:
                self._logger.warning(
                    "%s Attempts to (re)connect to bridge failed"
                    " - This might be an indication of connection issues.",
                    connect_attempts,
                )
            self._status = EventStreamStatus.CONNECTING
            await asyncio.sleep(reconnect_wait)

    async def __event_processor(self) -> NoReturn:
        """Process incoming Hue events on the Queue and distribute those."""
        while True:
            event: HueEvent = await self._event_queue.get()
            # each clip event has array of updated/added/deleted objects in data property
            # we fire an event for each object that was added/updated/deleted
            for item in event["data"]:
                self.emit(EventType(event["type"]), item)

    def __parse_message(self, msg: bytes) -> None:
        """Parse a plain message string as received from EventStream."""
        try:
            line = msg.decode().strip()
            if not line or ":" not in line:
                return
            key, value = line.split(":", 1)
            if not key:
                return
            if key == "id":
                self._last_event_id = value
                return
            if key == "data":
                # events is array with multiple events
                events: List[HueEvent] = json.loads(value)
                for event in events:
                    if event.get("type") not in ["add", "update", "delete"]:
                        raise InvalidEvent(f"Received invalid event {event}")
                    self._event_queue.put_nowait(event)
                return
            if key != "data":
                self._logger.debug("Received unexpected message: %s - %s", key, value)
        except Exception as exc:  # pylint: disable=broad-except
            self._logger.warning(
                "Unable to parse Event message: %s", line, exc_info=exc
            )

    async def __keepalive_workaround(self) -> NoReturn:
        """Send keepalive command to bridge, abusing geofence client."""
        # Oh yeah, this is a major hack and hopefully it will only be temporary ;-)
        # Signify forgot to implement some sort of periodic keep alive message on the EventBus
        # so we have no way to determine if the connection is still alive.
        # To workaround this, we create a geofence client (without a status)
        # on the bridge for aiohue which will have its name updated every minute
        # this will result in an event on the eventstream and thus a way to figure out
        # if its still alive. It's not very pretty but at least it works.
        # Now let's contact Signify if this can be solved.
        prefix = "aiohue_"

        while True:
            await asyncio.sleep(KEEPALIVE_INTERVAL)

            try:
                for client in self._bridge.sensors.geofence_client.items:
                    if client.name.startswith(prefix):
                        hass_client = client
                        break
                else:
                    await self._bridge.sensors.geofence_client.create(
                        GeofenceClientPost(name=prefix)
                    )
                    continue

                # simply updating the name of the geofence client will result in an event message
                # the eventstream timeout will detect if our keepalive message was not received
                random_str = "".join(
                    (random.choice(string.ascii_lowercase)) for x in range(10)
                )
                await self._bridge.sensors.geofence_client.update(
                    hass_client.id, GeofenceClientPut(name=f"{prefix}{random_str}")
                )
            except (ClientError, asyncio.TimeoutError, AiohueException) as err:
                # might happen on connection error, we don't want the retry logic to bail out
                self._logger.debug("Error while sending keepalive: %s", str(err))

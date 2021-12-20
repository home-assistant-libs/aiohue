"""Handle connecting to the HUE Eventstream and distribute events."""
from __future__ import annotations

import asyncio
import json
from asyncio.coroutines import iscoroutinefunction
from enum import Enum
from typing import TYPE_CHECKING, Callable, List, NoReturn, Tuple

from aiohttp import ClientTimeout
from aiohttp.client_exceptions import ClientError

if TYPE_CHECKING:
    from .. import HueBridgeV2

from ...errors import InvalidAPIVersion, InvalidEvent, Unauthorized
from ...util import NoneType
from ..models.clip import CLIPEvent, CLIPEventType, CLIPResource
from ..models.resource import ResourceTypes

CONNECTION_TIMEOUT = 30 * 60  # 30 minutes


class EventStreamStatus(Enum):
    """Status options of EventStream."""

    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2


class EventType(Enum):
    """Enum with possible Events (based on CLIPEventType)."""

    # overriding Enum is not possible but we want the event names to match
    RESOURCE_ADDED = CLIPEventType.RESOURCE_ADDED.value
    RESOURCE_UPDATED = CLIPEventType.RESOURCE_UPDATED.value
    RESOURCE_DELETED = CLIPEventType.RESOURCE_DELETED.value
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTED = "reconnected"


EventCallBackType = Callable[[EventType, CLIPResource], None]
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

    async def stop(self) -> None:
        """Stop listening for events."""
        for task in self._bg_tasks:
            task.cancel()
        self._bg_tasks = []

    def subscribe(
        self,
        callback: Callable[[EventType, CLIPResource | None], None],
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

    def emit(self, type: EventType, data: CLIPResource | None = None) -> None:
        """Emit event to all listeners."""
        for (callback, event_filter, resource_filter) in self._subscribers:
            if event_filter is not None and type not in event_filter:
                continue
            if (
                data is not None
                and resource_filter is not None
                and data.type not in resource_filter
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
        """Process incoming CLIPEvents on the Queue and distribute those."""
        while True:
            event: CLIPEvent = await self._event_queue.get()
            # each clip event has array of updated/added/deleted objects in data property
            # we fire an event for each object that was added/updated/deleted
            for item in event.data:
                self.emit(EventType(event.type.value), item)

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
                self._last_event_id = value.replace(":0", "")
                return
            if key == "data":
                # events is array with multiple events
                events: List[dict] = json.loads(value)
                for event in events:
                    clip_event = CLIPEvent.from_dict(event)
                    if clip_event.type == CLIPEventType.UNKNOWN:
                        raise InvalidEvent(
                            "Received invalid event %s", event.get("type")
                        )
                    self._event_queue.put_nowait(clip_event)
                return
            if key != "data":
                self._logger.debug("Received unexpected message: %s - %s", key, value)
        except Exception as exc:  # pylint: disable=broad-except
            self._logger.warning(
                "Unable to parse Event message: %s", line, exc_info=exc
            )

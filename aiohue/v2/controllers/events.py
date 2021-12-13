"""Handle connecting to the HUE Eventstream and distribute events."""
from __future__ import annotations
import asyncio
import json
from enum import Enum
from typing import TYPE_CHECKING, Callable, List, NoReturn, Tuple

from aiohttp.client_exceptions import ClientError
from asyncio.coroutines import iscoroutinefunction

if TYPE_CHECKING:
    from .. import HueBridgeV2

from ...util import NoneType
from ...errors import InvalidAPIVersion, InvalidEvent, Unauthorized
from ..models.clip import CLIPEvent, CLIPEventType, CLIPResource
from ..models.resource import ResourceTypes


class EventStreamStatus(Enum):
    """Status options of EventStream."""

    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2


EventType = CLIPEventType  # substitute
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
        callback: Callable[[EventType, CLIPResource], None],
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

    def emit(self, type: EventType, data: CLIPResource) -> None:
        """Emit event to all listeners."""
        for (callback, event_filter, resource_filter) in self._subscribers:
            if event_filter is not None and type not in event_filter:
                continue
            if resource_filter is not None and data.type not in resource_filter:
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
        headers = {"Accept": "text/event-stream", "Cache-Control": "no-cache"}
        retries = 0
        while True:
            if self._last_event_id:
                headers["Last-Event-ID"] = self._last_event_id
            try:
                async with self._bridge.create_request(
                    "get", "eventstream/clip/v2", timeout=0, headers=headers
                ) as resp:
                    # update status to connected once we reach this point
                    self._status = EventStreamStatus.CONNECTED
                    retries = 0  # reset on succesfull connect
                    self._logger.debug("Connected to EventStream")
                    # messages come in one by line, according to EventStream/SSE specs
                    # we iterate over the incoming lines in the streamreader.
                    # To prevent a deadlock waiting for a message while the connection is dead
                    # we have a simple timeout guard in place.
                    # If no message is received in 30 minutes, a Timeout error will be raised
                    # and thus the connection re-established.
                    iterator = resp.content.__aiter__()
                    while True:
                        line = await asyncio.wait_for(
                            iterator.__anext__(), timeout=30 * 60
                        )
                        self.__parse_message(line)
            except (ClientError, asyncio.TimeoutError) as err:
                status = getattr(err, "status", None)
                if status == 404:
                    raise InvalidAPIVersion from err
                if status == 403:
                    raise Unauthorized from err
                # pass all other errors because we will auto retry
            finally:
                self._status = EventStreamStatus.CONNECTING
                retries += 1
                await asyncio.sleep(2 * retries)

    async def __event_processor(self) -> NoReturn:
        """Process incoming CLIPEvents on the Queue and distribute those."""
        while True:
            event: CLIPEvent = await self._event_queue.get()
            # each clip event has array of updated/added/deleted objects in data property
            # we fire an event for each object that was added/updated/deleted
            for item in event.data:
                self.emit(EventType(event.type), item)

    def __parse_message(self, line: bytes) -> None:
        """Parse a plain message string as received from EventStream."""
        try:
            line = line.decode().strip()
            if not line or ":" not in line:
                return
            key, value = line.split(":", 1)
            if not key:
                return
            if key == "id":
                self._last_event_id = value.replace(":0", "")
                return
            if key == "data":
                # events is array with multiple events (but contains just one)
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

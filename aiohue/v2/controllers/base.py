"""Base controller for HUE resources as retrieved from the Hue bridge."""
from __future__ import annotations

import asyncio
from asyncio.coroutines import iscoroutinefunction
from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, Iterator, List, Tuple

from aiohue.v2.models.device import Device

from ...util import NoneType, dataclass_to_dict, update_dataclass
from ..models.clip import CLIPResource, parse_clip_resource
from ..models.resource import ResourceTypes
from .events import EventCallBackType, EventType

if TYPE_CHECKING:
    from .. import HueBridgeV2


EventSubscriptionType = Tuple[
    EventCallBackType,
    "Tuple[EventType] | None",
]

ID_FILTER_ALL = "*"


class BaseResourcesController(Generic[CLIPResource]):
    """Holds and manages all items for a specific Hue resource type."""

    item_type = ResourceTypes.UNKNOWN

    def __init__(self, bridge: "HueBridgeV2") -> None:
        """Initialize instance."""
        self._bridge = bridge
        self._items: Dict[str, CLIPResource] = {}
        self._logger = bridge.logger.getChild(self.item_type.value)
        self._subscribers: Dict[str, EventSubscriptionType] = {ID_FILTER_ALL: []}
        self._initialized = False

    @property
    def items(self) -> List[CLIPResource]:
        """Return all items for this resource."""
        return list(self._items.values())

    async def initialize(self, initial_data: List[dict] | None) -> None:
        """
        Initialize controller by fetching all items for this resource type from bridge.

        Must be called only once. Any updates will be retrieved by events.
        Optionally provide the initial data.
        """
        if initial_data is None:
            endpoint = f"clip/v2/resource/{self.item_type.value}"
            initial_data = await self._bridge.request("get", endpoint)
        else:
            initial_data = [
                x for x in initial_data if x["type"] == self.item_type.value
            ]
        self._logger.debug("fetched %s items", len(initial_data))

        if self._initialized:
            # we're already initialized, treat this as reconnect
            await self.__handle_reconnect(initial_data)
            return

        for item in initial_data:
            resource: CLIPResource = parse_clip_resource(item)
            self._items[resource.id] = resource
        # subscribe to item updates
        self._bridge.events.subscribe(
            self._handle_event, resource_filter=self.item_type
        )
        self._initialized = True

    def subscribe(
        self,
        callback: EventCallBackType,
        id_filter: str | Tuple[str] | None = None,
        event_filter: EventType | Tuple[EventType] | None = None,
    ) -> Callable:
        """
        Subscribe to status changes for this resource type.

        Parameters:
            - `callback` - callback function to call when an event emits.
            - `id_filter` - Optionally provide resource ID(s) to filter events for.
            - `event_filter` - Optionally provide EventType(s) as filter.

        Returns:
            function to unsubscribe.
        """
        if not isinstance(event_filter, (NoneType, (list, tuple))):
            event_filter = (event_filter,)

        if id_filter is None:
            id_filter = (ID_FILTER_ALL,)
        elif not isinstance(id_filter, (list, tuple)):
            id_filter = (id_filter,)

        subscription = (callback, event_filter)

        for id_key in id_filter:
            if id_key not in self._subscribers:
                self._subscribers[id_key] = []
            self._subscribers[id_key].append(subscription)

        # unsubscribe logic
        def unsubscribe():
            for id_key in id_filter:
                if id_key not in self._subscribers:
                    continue
                self._subscribers[id_key].remove(subscription)

        return unsubscribe

    def get_by_v1_id(self, id: str) -> CLIPResource | None:
        """Get item by it's legacy V1 id."""
        return next((item for item in self._items.values() if item.id_v1 == id), None)

    def get_device(self, id: str) -> Device | None:
        """
        Return device the given resource belongs to.

        Returns None if the resource id is (no longer) valid
        or does not belong to a device.
        """
        if self.item_type == ResourceTypes.DEVICE:
            return self[id]
        for device in self._bridge.devices:
            for service in device.services:
                if service.rid == id:
                    return device
        return None

    async def update(self, id: str, obj_in: CLIPResource) -> None:
        """
        Update HUE resource with PUT command.

        Provide instance of object's class with only the changed keys set.
        Note that not all resources allow updating/setting of data.
        Sending keys that are not allowed, results in an error from the bridge.
        """
        endpoint = f"clip/v2/resource/{self.item_type.value}/{id}"
        # create a clean dict with only the changed keys set.
        data = dataclass_to_dict(obj_in, skip_none=True)
        await self._bridge.request("put", endpoint, json=data)

    async def create(self, id: str, obj_in: CLIPResource) -> None:
        """
        Create HUE resource with POST command.

        Provide instance of object's class with only the required/allowed keys set.
        Note that not all resources allow creating of items.
        Sending keys that are not allowed, results in an error from the bridge.
        """
        endpoint = f"clip/v2/resource/{self.item_type.value}/{id}"
        # create a clean dict with only the not None keys set.
        data = dataclass_to_dict(obj_in, skip_none=True)
        await self._bridge.request("post", endpoint, json=data)

    def get(self, id: str, default: Any = None) -> CLIPResource | None:
        """Get item by id of default if item does not exist."""
        return self._items.get(id, default)

    def __getitem__(self, id: str) -> CLIPResource:
        """Get item by id."""
        return self._items[id]

    def __iter__(self) -> Iterator[CLIPResource]:
        """Iterate items."""
        return iter(self._items.values())

    def __contains__(self, id: str) -> bool:
        """Return bool if id is in items."""
        return id in self._items

    async def _handle_event(self, type: EventType, item: CLIPResource | None) -> None:
        """Handle incoming event for this resource from the EventStream."""
        if type == EventType.RESOURCE_ADDED:
            # new item added
            cur_item = self._items[item.id] = item
        elif type == EventType.RESOURCE_DELETED:
            # existing item deleted
            cur_item = self._items.pop(item.id, item)
        elif type == EventType.RESOURCE_UPDATED:
            # existing item updated
            cur_item = self._items.get(item.id)
            if cur_item is None:
                # should not be possible but just in case
                # if this does happen often we should consider fetching the full object
                self._logger.warning("received update for unknown item %s", item.id)
                return
            # make sure we only update keys that are not None
            update_dataclass(cur_item, item)
        else:
            # ignore all other events
            return

        subscribers = (
            self._subscribers.get(item.id, []) + self._subscribers[ID_FILTER_ALL]
        )
        for (callback, event_filter) in subscribers:
            if event_filter is not None and type not in event_filter:
                continue
            # dispatch the full resource object to the callback
            if iscoroutinefunction(callback):
                asyncio.create_task(callback(type, item))
            callback(type, cur_item)

    async def __handle_reconnect(self, full_state: List[dict]) -> None:
        """Force update of state (on reconnect)."""
        # When a reconnect (of the eventstream) happens our state can't be trusted
        # We need to fetch the full state to check what changed
        # NOTE: This should actually be managed by the `Last-Event-ID` on the SSE
        # but seems like Hue did not implement that on the bridge.
        prev_ids = set(self._items.keys())
        cur_ids = set()
        for item in full_state:
            resource: CLIPResource = parse_clip_resource(item)
            cur_ids.add(resource.id)
            if resource.id not in prev_ids:
                # item added
                await self._handle_event(EventType.RESOURCE_ADDED, resource)
            else:
                # work out if the item actually changed
                prev_item = self._items[resource.id]
                if dataclass_to_dict(prev_item) == dataclass_to_dict(resource):
                    continue
                await self._handle_event(EventType.RESOURCE_UPDATED, resource)
        # work out item deletions
        deleted_ids = {x for x in prev_ids if x not in cur_ids}
        for resource_id in deleted_ids:
            self._handle_event(EventType.RESOURCE_DELETED, self._items[resource_id])


class GroupedControllerBase(Generic[CLIPResource]):
    """Convenience controller which combines items from multiple resources."""

    def __init__(
        self, bridge: "HueBridgeV2", resources: List[BaseResourcesController]
    ) -> None:
        """Initialize instance."""
        self._resources = resources
        self._bridge = bridge
        self._logger = bridge.logger.getChild(self.__class__.__name__.lower())
        self._subscribers: List[Tuple[EventCallBackType, str | None]] = []

    @property
    def resources(self) -> List[BaseResourcesController]:
        """Return all resource controllers that are grouped by this groupcontroller."""
        return self._resources

    @property
    def items(self) -> List[CLIPResource]:
        """Return all items from all grouped resources."""
        return [x for y in self._resources for x in y]

    def subscribe(
        self,
        callback: EventCallBackType,
        id_filter: str | Tuple[str] | None = None,
        event_filter: EventType | Tuple[EventType] | None = None,
    ) -> Callable:
        """Subscribe to status changes for all grouped resources."""
        unsubs = [
            x.subscribe(callback, id_filter, event_filter) for x in self._resources
        ]

        def unsubscribe():
            for unsub in unsubs:
                unsub()

        return unsubscribe

    async def initialize(self, initial_data: List[dict] | None) -> None:
        """Initialize controller for all watched resources."""
        for resource_control in self._resources:
            await resource_control.initialize(initial_data)

    def get(self, id: str, default: Any = None) -> CLIPResource | None:
        """Get item by id of default if item does not exist."""
        return next((x for y in self._resources for x in y if x.id == id), default)

    def __getitem__(self, id: str) -> CLIPResource:
        """Get item by id."""
        return next((x for y in self._resources for x in y if x.id == id))

    def __iter__(self) -> Iterator[CLIPResource]:
        """Iterate items."""
        return iter(self.items)

    def __contains__(self, id: str) -> bool:
        """Return bool if id is in items."""
        return any((x for x in self.items if x.id == id))

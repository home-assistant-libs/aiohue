"""Base controller for HUE resources as retrieved from the Hue bridge."""

import asyncio
from typing import TYPE_CHECKING, Callable, Dict, Generic, Iterator, List, Tuple

from ...util import to_dict, update_dataclass

from ..models.clip import CLIPResource, parse_clip_resource
from ..models.resource import ResourceTypes
from .events import EventCallBackType, EventType


if TYPE_CHECKING:
    from .. import HueBridgeV2


class BaseResourcesController(Generic[CLIPResource]):
    """Holds and manages all items for a specific Hue resource type."""

    item_type = ResourceTypes.UNKNOWN

    def __init__(self, bridge: "HueBridgeV2") -> None:
        """Initialize instance."""
        self.bridge = bridge
        self._items: Dict[str, CLIPResource] = {}
        self.logger = bridge.logger.getChild(self.item_type.value)
        self._subscribers: List[Tuple[EventCallBackType, str | None]] = []

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
            initial_data = await self.bridge.request("get", endpoint)
        item_count = 0
        for item in initial_data:
            if ResourceTypes(item["type"]) != self.item_type:
                continue
            item_count += 1
            res: CLIPResource = parse_clip_resource(item)
            if res is None:
                continue
            self._items[str(res.id)] = res
        # subscribe to item updates
        self.bridge.events.subscribe(
            self.__handle_event, resource_filter=self.item_type
        )
        self.logger.debug("fetched %s items", item_count)

    def subscribe(
        self,
        callback: EventCallBackType,
        id_filter: str | None = None,
    ) -> Callable:
        """
        Subscribe to status changes for this resource type.

        Parameters:
            - `id_filter` - Optionally provide a resource ID to filter events for.

        Returns:
            function to unsubscribe.
        """
        subscription = (callback, id_filter)

        def unsubscribe():
            self._subscribers.remove(subscription)

        self._subscribers.append(subscription)
        return unsubscribe

    def get_by_v1_id(self, id: str) -> CLIPResource | None:
        """Get item by it's legacy V1 id."""
        return next((item.v1_id == id for item in self._items.values()), None)

    async def _send_put(self, id: str, obj_in: CLIPResource) -> None:
        """
        Update HUE resource with PUT command.

        Provide instance of object's class with only the changed key set.
        Note that not all resources allow updating/setting of data.
        """
        endpoint = f"clip/v2/resource/{self.item_type.value}/{id}"
        # create a clean dict with only the changed keys set.
        data = to_dict(obj_in)
        asyncio.create_task(self.bridge.request("put", endpoint, json=data))

    def __getitem__(self, id: str) -> CLIPResource:
        """Get item by id."""
        return self._items[str(id)]

    def __iter__(self) -> Iterator[CLIPResource]:
        """Iterate items."""
        return iter(self._items.values())

    def __handle_event(self, type: EventType, item: CLIPResource) -> None:
        """Handle incoming event for this resource from the EventStream."""
        if type == EventType.RESOURCE_ADDED:
            # new item added
            cur_item = self._items[item.id] = item
        elif type == EventType.RESOURCE_DELETED:
            # existing item deleted
            cur_item = self._items.pop(item.id, item)
        else:
            # existing item updated
            cur_item = self._items.get(item.id)
            if cur_item is None:
                # should not be possible but just in case
                # if this does happen often we should consider fetching the full object here
                self.logger.warning("received update for unknown item %s", item.id)
                return
            # make sure we only update keys that are not None
            update_dataclass(cur_item, item)

        for (callback, id_filter) in self._subscribers:
            if id_filter is not None and str(id_filter) != str(item.id):
                continue
            # dispatch the full resource object to the callback
            callback(type, cur_item)


class GroupedControllerBase(Generic[CLIPResource]):
    """Convenience controller which combines items from multiple resources."""

    def __init__(
        self, bridge: "HueBridgeV2", resources: List[BaseResourcesController]
    ) -> None:
        """Initialize instance."""
        self._resources = resources
        self.bridge = bridge
        self.logger = bridge.logger.getChild(self.__class__.__name__.lower())
        self._subscribers: List[Tuple[EventCallBackType, str | None]] = []

    @property
    def items(self) -> List[CLIPResource]:
        """Return all items from all watched resources."""
        return [x for y in self._resources for x in y]

    def subscribe(
        self,
        callback: EventCallBackType,
        id_filter: str | None = None,
    ) -> Callable:
        """Subscribe to status changes for all watched resource."""
        unsubs = [x.subscribe(callback, id_filter) for x in self._resources]

        def unsubscribe():
            for unsub in unsubs:
                unsub()

        return unsubscribe

    async def initialize(self, initial_data: List[dict] | None) -> None:
        """Initialize controller for all watched resources."""
        for resource_control in self._resources:
            await resource_control.initialize(initial_data)

    def __getitem__(self, id: str) -> CLIPResource:
        """Get item by id."""
        return next((x.id == id for x in self.items))

    def __iter__(self) -> Iterator[CLIPResource]:
        """Iterate items."""
        return iter(self.items)

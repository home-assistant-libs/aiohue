"""Base controller for HUE resources as retrieved from the Hue bridge."""

import asyncio
from collections.abc import Callable, Iterator
from inspect import iscoroutinefunction

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
)

from aiohue.util import (
    NoneType,
    dataclass_from_dict,
    dataclass_to_dict,
    update_dataclass,
)
from aiohue.v2.models.device import Device
from aiohue.v2.models.resource import ResourceTypes

from .events import EventCallBackType, EventType

if TYPE_CHECKING:
    from aiohue.v2 import HueBridgeV2


EventSubscriptionType = tuple[
    EventCallBackType,
    "tuple[EventType] | None",
]

ID_FILTER_ALL = "*"

CLIPResource = TypeVar("CLIPResource")


class BaseResourcesController(Generic[CLIPResource]):
    """Holds and manages all items for a specific Hue resource type."""

    item_type: ResourceTypes | None = None
    item_cls: CLIPResource | None = None
    allow_parser_error = False

    def __init__(self, bridge: "HueBridgeV2") -> None:
        """Initialize instance."""
        self._bridge = bridge
        self._items: dict[str, CLIPResource] = {}
        self._logger = bridge.logger.getChild(self.item_type.value)
        self._subscribers: dict[str, EventSubscriptionType] = {ID_FILTER_ALL: []}
        self._initialized = False

    @property
    def items(self) -> list[CLIPResource]:
        """Return all items for this resource."""
        return list(self._items.values())

    async def initialize(self, initial_data: list[dict] | None) -> None:
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
            await self._handle_event(EventType.RESOURCE_ADDED, item)
        # subscribe to item updates
        self._bridge.events.subscribe(
            self._handle_event, resource_filter=self.item_type
        )
        self._initialized = True

    def subscribe(
        self,
        callback: EventCallBackType,
        id_filter: str | tuple[str] | None = None,
        event_filter: EventType | tuple[EventType] | None = None,
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
        if not isinstance(event_filter, NoneType | list | tuple):
            event_filter = (event_filter,)

        if id_filter is None:
            id_filter = (ID_FILTER_ALL,)
        elif not isinstance(id_filter, list | tuple):
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

    async def create(self, obj_in: CLIPResource) -> None:
        """
        Create HUE resource with POST command.

        Provide instance of object's class with only the required/allowed keys set.
        Note that not all resources allow creating of items.
        Sending keys that are not allowed, results in an error from the bridge.
        """
        endpoint = f"clip/v2/resource/{self.item_type.value}"
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

    async def _handle_event(
        self, evt_type: EventType, evt_data: dict | None, is_reconnect: bool = False
    ) -> None:
        """Handle incoming event for this resource from the EventStream."""
        # pylint: disable=too-many-return-statements,too-many-branches
        if evt_data is None:
            return
        item_id = evt_data.get("rid", evt_data["id"])
        if evt_type == EventType.RESOURCE_ADDED:
            # new item added
            try:
                cur_item = self._items[item_id] = dataclass_from_dict(
                    self.item_cls, evt_data
                )
            except (KeyError, ValueError, TypeError) as exc:
                # In an attempt to not completely crash when a single resource can't be parsed
                # due to API schema mismatches, bugs in Hue or other factors, we allow some
                # resources to be skipped. This only works for resources that are not dependees
                # for other resources so we define this in the controller level.
                if not self.allow_parser_error:
                    raise exc
                self._logger.error(
                    "Unable to parse resource, please report this to the authors of aiohue.",
                    exc_info=exc,
                )
                return
        elif evt_type == EventType.RESOURCE_DELETED:
            # existing item deleted
            cur_item = self._items.pop(item_id, evt_data)
        elif evt_type == EventType.RESOURCE_UPDATED:
            # existing item updated
            cur_item = self._items.get(item_id)
            if cur_item is None:
                # should not be possible but just in case
                # if this does happen often we should consider fetching the full object
                self._logger.warning("received update for unknown item %s", item_id)
                return
            # update the existing data with the changed keys/data
            updated_keys = update_dataclass(cur_item, evt_data)
            # do not forward update event at reconnects if no keys were updated
            if len(updated_keys) == 0 and is_reconnect:
                return

            # Do not forward update events for button resource if
            # the button feature is missing in event data in an attempt to prevent
            # ghost events at bridge reboots/firmware updates.
            # in fact this is a feature request to Signify to handle these stateless
            # device events in a different way:
            # https://developers.meethue.com/forum/t/differentiate-stateless-events/6627
            if self.item_type == ResourceTypes.BUTTON and not evt_data.get(
                "button", {}
            ).get("button_report"):
                return
            if self.item_type == ResourceTypes.RELATIVE_ROTARY and not evt_data.get(
                "relative_rotary", {}
            ).get("rotary_report"):
                return
        else:
            # ignore all other events
            return

        subscribers = (
            self._subscribers.get(item_id, []) + self._subscribers[ID_FILTER_ALL]
        )
        for callback, event_filter in subscribers:
            if event_filter is not None and evt_type not in event_filter:
                continue
            # dispatch the full resource object to the callback
            if iscoroutinefunction(callback):
                asyncio.create_task(callback(evt_type, cur_item))
            else:
                callback(evt_type, cur_item)

    async def __handle_reconnect(self, full_state: list[dict]) -> None:
        """Force update of state (on reconnect)."""
        # When the connection to the eventstream was lost for a longer time
        # we fetch the full state to check what changed
        # NOTE: Short connection drops are handled by the `Last-Event-Id` mechanism.
        prev_ids = set(self._items.keys())
        cur_ids = set()
        for item in full_state:
            cur_ids.add(item["id"])
            if item["id"] not in prev_ids:
                # item added
                await self._handle_event(EventType.RESOURCE_ADDED, item)
            else:
                # work out if the item changed in the regular event logic
                # ignore stateless (button) resources to prevent false positive state events
                if item["type"] in (
                    ResourceTypes.BUTTON.value,
                    ResourceTypes.RELATIVE_ROTARY.value,
                ):
                    continue
                await self._handle_event(
                    EventType.RESOURCE_UPDATED, item, is_reconnect=True
                )

        # work out item deletions
        deleted_ids = {x for x in prev_ids if x not in cur_ids}
        for resource_id in deleted_ids:
            self._handle_event(
                EventType.RESOURCE_DELETED,
                {"rtype": self.item_type, "rid": resource_id},
            )


class GroupedControllerBase(Generic[CLIPResource]):
    """Convenience controller which combines items from multiple resources."""

    def __init__(
        self, bridge: "HueBridgeV2", resources: list[BaseResourcesController]
    ) -> None:
        """Initialize instance."""
        self._resources = resources
        self._bridge = bridge
        self._logger = bridge.logger.getChild(self.__class__.__name__.lower())
        self._subscribers: list[tuple[EventCallBackType, str | None]] = []

    @property
    def resources(self) -> list[BaseResourcesController]:
        """Return all resource controllers that are grouped by this groupcontroller."""
        return self._resources

    @property
    def items(self) -> list[CLIPResource]:
        """Return all items from all grouped resources."""
        return [x for y in self._resources for x in y]

    def subscribe(
        self,
        callback: EventCallBackType,
        id_filter: str | tuple[str] | None = None,
        event_filter: EventType | tuple[EventType] | None = None,
    ) -> Callable:
        """Subscribe to status changes for all grouped resources."""
        unsubs = [
            x.subscribe(callback, id_filter, event_filter) for x in self._resources
        ]

        def unsubscribe():
            for unsub in unsubs:
                unsub()

        return unsubscribe

    async def initialize(self, initial_data: list[dict] | None) -> None:
        """Initialize controller for all watched resources."""
        for resource_control in self._resources:
            await resource_control.initialize(initial_data)

    def get_device(self, id: str) -> Device | None:
        """
        Return device the given resource belongs to.

        Returns None if the resource id is (no longer) valid
        or does not belong to a device.
        """
        for ctrl in self._resources:
            if id in ctrl:
                return ctrl.get_device(id)
        return None

    def get(self, id: str, default: Any = None) -> CLIPResource | None:
        """Get item by id of default if item does not exist."""
        return next((x for y in self._resources for x in y if x.id == id), default)

    def __getitem__(self, id: str) -> CLIPResource:
        """Get item by id."""
        return next(x for y in self._resources for x in y if x.id == id)

    def __iter__(self) -> Iterator[CLIPResource]:
        """Iterate items."""
        return iter(self.items)

    def __contains__(self, id: str) -> bool:
        """Return bool if id is in items."""
        return any(x for x in self.items if x.id == id)

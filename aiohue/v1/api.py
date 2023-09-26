from __future__ import annotations


class APIItems:
    """Base class for a map of API Items."""

    def __init__(self, logger, raw, request, path, item_cls):
        self._logger = logger
        self._request = request
        self._path = path
        self._item_cls = item_cls
        self._items = {}
        self._process_raw(raw)

    @property
    def items(self):
        return self.values()

    async def update(self):
        """Request update of all items of this resource type."""
        raw = await self._request("get", self._path)
        self._process_raw(raw)

    def _process_raw(self, raw):
        for id, raw_item in raw.items():
            obj = self._items.get(id)

            if obj is not None:
                obj.raw = raw_item
            else:
                self._items[id] = self._item_cls(
                    id,
                    raw_item,
                    self._request,
                )

        removed_items = []

        for id in self._items:
            if id not in raw:
                removed_items.append(id)

        for id in removed_items:
            del self._items[id]

    def values(self):
        return list(self._items.values())

    def __getitem__(self, obj_id):
        return self._items[obj_id]

    def __iter__(self):
        return iter(self._items)

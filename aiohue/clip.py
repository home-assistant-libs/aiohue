import json
import logging


class Clip:
    """Represent Hue clip."""

    def __init__(self, request_2):
        self._request_2 = request_2

    async def stream_events(self, last_event_id=None):
        """Async iterate over the incoming events.

        https://nchan.io/#eventsource
        """
        kwargs = {"headers": {"Accept": "text/event-stream"}, "timeout": 0}
        if last_event_id is not None:
            kwargs["headers"]["Last-Event-ID"] = last_event_id

        async with self._request_2(
            "get",
            "eventstream/clip/v2",
            **kwargs,
        ) as resp:
            event = {}
            # First event is `{"": "hi"}`, which we will skip.
            skip_event = True

            async for line in resp.content:
                line = line.decode().strip()

                # Object finished.
                if not line:
                    if skip_event:
                        skip_event = False
                    else:
                        yield event

                    continue

                elif skip_event:
                    continue

                try:
                    key, value = line.split(": ", 1)
                    if key == "data":
                        value = json.loads(value)
                    event[key] = value
                except ValueError:
                    logging.getLogger(__name__).error("Unexpected event data: %s", line)
                    skip_event = True
                    event = {}

    async def resources(self):
        """Fetch resources from Hue.

        Available types:

        homekit
        device
        bridge
        zigbee_connectivity
        entertainment
        light
        bridge_home
        grouped_light
        room
        scene
        """
        async with self._request_2("get", "clip/v2/resource") as resp:
            return await resp.json()

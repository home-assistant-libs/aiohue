class Clip:
    """Represent Hue clip."""

    def __init__(self, request_2):
        self._request_2 = request_2

    async def next_events(self):
        """Note, this method will be pending until next event."""
        return await self._request_2("get", "eventstream/clip/v2", timeout=None)

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
        return await self._request_2("get", "clip/v2/resource")

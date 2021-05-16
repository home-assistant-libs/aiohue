class Config:
    """Represent Hue config.

    https://developers.meethue.com/documentation/configuration-api#72_get_configuration
    """

    def __init__(self, raw, request):
        self.raw = raw
        self._request = request

    @property
    def name(self):
        """Name of the bridge."""
        return self.raw["name"]

    @property
    def swversion(self):
        """Software version of the bridge."""
        return self.raw["swversion"]

    @property
    def swupdate2_bridge_state(self):
        """Software update state of the bridge."""
        return self.raw.get("swupdate2", {}).get("bridge", {}).get("state")

    @property
    def modelid(self):
        """Model ID of the bridge."""
        return self.raw["modelid"]

    @property
    def bridgeid(self):
        """ID of the bridge."""
        return self.raw["bridgeid"]

    @property
    def apiversion(self):
        """Supported API version of the bridge."""
        return self.raw["apiversion"]

    @property
    def mac(self):
        """Mac address of the bridge."""
        return self.raw["mac"]

    async def update(self):
        self.raw = await self._request("get", "config")

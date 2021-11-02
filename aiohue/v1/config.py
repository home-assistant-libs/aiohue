"""Controller/model for Hue resource of type Config."""
from __future__ import annotations

from typing import Any, Coroutine, Dict


class Config:
    """
    Represent Hue config.

    https://developers.meethue.com/documentation/configuration-api#72_get_configuration
    """

    def __init__(self, raw: Dict[str, Any], request: Coroutine) -> None:
        """Initialize Config resource controller."""
        self.raw = raw
        self._request = request
        self.bridgeid = self.bridge_id  # for backwards compatability
        self.mac = self.mac_address  # for backwards compatability
        self.modelid = self.model_id  # for backwards compatability
        self.swversion = self.software_version  # for backwards compatability

    @property
    def bridge_id(self) -> str:
        """ID of the bridge."""
        return self.raw["bridgeid"]

    @property
    def name(self) -> str:
        """Name of the bridge."""
        return self.raw["name"]

    @property
    def mac_address(self) -> str:
        """Mac address of the bridge."""
        return self.raw["mac"]

    @property
    def model_id(self) -> str:
        """Model ID of the bridge."""
        return self.raw["modelid"]

    @property
    def software_version(self) -> str:
        """Software version of the bridge."""
        return self.raw["swversion"]

    @property
    def swupdate2_bridge_state(self) -> str:
        """Software update state of the bridge."""
        return self.raw.get("swupdate2", {}).get("bridge", {}).get("state")

    @property
    def apiversion(self) -> str:
        """Supported API version of the bridge."""
        return self.raw["apiversion"]

    async def update(self) -> None:
        """Update data for this resource."""
        self.raw = await self._request("get", "config")

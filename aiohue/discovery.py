"""Discover Hue bridge(s) with NUPNP."""
from dataclasses import dataclass

from aiohttp import ClientSession

from .util import normalize_bridge_id

URL_NUPNP = "https://discovery.meethue.com/"


@dataclass(frozen=True)
class DiscoveredHueBridge:
    """Model for a discovered Hue bridge."""

    host: str
    id: str


async def discover_nupnp(websession: ClientSession | None = None):
    """Discover bridges via NUPNP."""
    websession_provided = websession is not None
    if websession is None:
        websession = ClientSession()
    try:
        async with websession.get(URL_NUPNP) as res:
            return [
                DiscoveredHueBridge(
                    item["internalipaddress"],
                    bridge_id=normalize_bridge_id(item["id"]),
                )
                for item in (await res.json())
            ]
    finally:
        if not websession_provided:
            await websession.close()

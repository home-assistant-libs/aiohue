"""Discover Hue bridge(s) with NUPNP."""
from dataclasses import dataclass
from typing import List

from aiohttp import ClientSession
from .util import is_v2_bridge

URL_NUPNP = "https://discovery.meethue.com/"


@dataclass(frozen=True)
class DiscoveredHueBridge:
    """Model for a discovered Hue bridge."""

    host: str
    id: str
    supports_v2: bool


async def discover_nupnp(
    websession: ClientSession | None = None,
) -> List[DiscoveredHueBridge]:
    """Discover bridges via NUPNP."""
    result = []
    websession_provided = websession is not None
    if websession is None:
        websession = ClientSession()
    try:
        async with websession.get(URL_NUPNP, timeout=5) as res:
            for item in await res.json():
                host = item["internalipaddress"]
                # the nupnp discovery might return items that are not in local network
                # connect to each bridge to find out if it's alive.
                bridge_id = await is_hue_bridge(host, websession)
                if bridge_id is None:
                    continue
                supports_v2 = await is_v2_bridge(host, websession)
                result.append(
                    DiscoveredHueBridge(host, bridge_id, supports_v2),
                )
        return result
    finally:
        if not websession_provided:
            await websession.close()


async def is_hue_bridge(
    host: str, websession: ClientSession | None = None
) -> str | None:
    """Check if there is a bridge alive on given ip and return bridge ID."""
    websession_provided = websession is not None
    if websession is None:
        websession = ClientSession()
    try:
        # every hue bridge returns discovery info on this endpoint
        url = f"http://{host}/api/config"
        async with websession.get(url, timeout=1) as res:
            assert res.status == 200
            data = await res.json()
            return data["bridgeid"]
    except Exception:  # pylint: disable=broad-except
        return None
    finally:
        if not websession_provided:
            await websession.close()

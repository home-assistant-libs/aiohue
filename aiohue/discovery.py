"""Various helper utility for Hue bridge discovery."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List

from aiohttp import ClientSession

from .util import normalize_bridge_id

URL_NUPNP = "https://discovery.meethue.com/"


@dataclass(frozen=True)
class DiscoveredHueBridge:
    """Model for a discovered Hue bridge."""

    host: str
    id: str
    supports_v2: bool


async def discover_bridge(
    host: str,
    websession: ClientSession | None = None,
) -> DiscoveredHueBridge:
    """
    Discover bridge details from given hostname/ip.

    Raises exception from aiohttp if there is no bridge alive on given ip/host.
    """
    websession_provided = websession is not None
    if websession is None:
        websession = ClientSession()
    try:
        bridge_id = await is_hue_bridge(host, websession)
        supports_v2 = await is_v2_bridge(host, websession)
        return DiscoveredHueBridge(host, bridge_id, supports_v2)
    finally:
        if not websession_provided:
            await websession.close()


async def discover_nupnp(
    websession: ClientSession | None = None,
) -> List[DiscoveredHueBridge]:
    """Discover bridges via NUPNP."""
    result = []
    websession_provided = websession is not None
    if websession is None:
        websession = ClientSession()
    try:
        async with websession.get(URL_NUPNP, timeout=30) as res:
            for item in await res.json():
                host = item["internalipaddress"]
                # the nupnp discovery might return items that are not in local network
                # connect to each bridge to find out if it's alive.
                try:
                    result.append(await discover_bridge(host, websession))
                except Exception:  # noqa
                    pass
        return result
    finally:
        if not websession_provided:
            await websession.close()


async def is_hue_bridge(host: str, websession: ClientSession | None = None) -> str:
    """
    Check if there is a bridge alive on given ip and return bridge ID.

    Raises exception from aiohttp if the bridge can not be reached on given hostname.
    """
    websession_provided = websession is not None
    if websession is None:
        websession = ClientSession()
    try:
        # every hue bridge returns discovery info on this endpoint
        url = f"http://{host}/api/config"
        async with websession.get(url, timeout=30) as res:
            res.raise_for_status()
            data = await res.json()
            return normalize_bridge_id(data["bridgeid"])
    finally:
        if not websession_provided:
            await websession.close()


async def is_v2_bridge(host: str, websession: ClientSession | None = None) -> bool:
    """Check if the bridge has support for the new V2 api."""
    websession_provided = websession is not None
    if websession is None:
        websession = ClientSession()
    try:
        # v2 api is https only and returns a 403 forbidden when no key provided
        url = f"https://{host}/clip/v2/resources"
        async with websession.get(
            url, ssl=False, raise_for_status=False, timeout=30
        ) as res:
            return res.status == 403
    except Exception:  # pylint: disable=broad-except
        # all other status/exceptions means the bridge is not v2 or not reachable at this time
        return False
    finally:
        if not websession_provided:
            await websession.close()

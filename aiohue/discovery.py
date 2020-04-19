from .bridge import Bridge
from .util import normalize_bridge_id

URL_NUPNP = "https://discovery.meethue.com/"


async def discover_nupnp(websession):
    """Discover bridges via NUPNP."""
    async with websession.get(URL_NUPNP) as res:
        return [
            Bridge(
                item["internalipaddress"],
                bridge_id=normalize_bridge_id(item["id"]),
                websession=websession,
            )
            for item in (await res.json())
        ]

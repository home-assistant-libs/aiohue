import async_timeout
import aiohttp

from .bridge import Bridge
from .util import get_websession

URL_NUPNP = 'https://www.meethue.com/api/nupnp'


async def discover_nupnp(*, websession: aiohttp.ClientSession = None):
    """Discover bridges via NUPNP."""
    if websession is None:
        websession = get_websession()

    async with async_timeout.timeout(10):
        async with websession.get(URL_NUPNP) as res:
            return [Bridge(item['internalipaddress'], websession=websession)
                    for item in (await res.json())]

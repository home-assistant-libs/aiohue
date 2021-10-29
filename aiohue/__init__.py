
from aiohttp import ClientSession
from .v1 import HueBridgeV1  # noqa
from .v2 import HueBridgeV2  # noqa
from .errors import *  # noqa


async def is_v2_bridge(host: str, websession: ClientSession | None = None) -> bool:
    """Check if the bridge has support for the new V2 api."""
    websession_provided = websession is not None
    if websession is None:
        websession = ClientSession()
    try:
        # v2 api is https only and returns a 403 forbidden when no key provided
        url = f"https://{host}/clip/v2/resources"
        async with websession.get(url) as res:
            return res.status == 403
    except Exception:  # pylint: disable=broad-except
        return False
    finally:
        if not websession_provided:
            await websession.close()

import asyncio

import aiohttp

_SESSION = None  # type: aiohttp.ClientSession


def get_websession():
    """Return a websession to use."""
    global _SESSION

    if _SESSION is not None:
        return _SESSION

    import atexit

    loop = asyncio.get_event_loop()
    _SESSION = aiohttp.ClientSession(loop=loop)
    atexit.register(lambda: loop.run_until_complete(_SESSION.close()))
    return _SESSION

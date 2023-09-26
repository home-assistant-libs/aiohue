"""AIOHue example for HUE bridge discovery."""
import asyncio
from os.path import abspath, dirname
from sys import path

path.insert(1, dirname(dirname(abspath(__file__))))

import contextlib  # noqa: E402

from aiohue.discovery import discover_nupnp  # noqa: E402


async def main():
    """Run code example."""
    discovered_bridges = await discover_nupnp()
    print()
    print("Discovered bridges:")
    for item in discovered_bridges:
        print()
        print(item)
        print()


with contextlib.suppress(KeyboardInterrupt):
    asyncio.run(main())

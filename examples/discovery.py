"""AIOHue example for HUE bridge discovery."""

import asyncio
import contextlib

from aiohue.discovery import discover_nupnp


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

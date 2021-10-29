"""AIOHue example for HUE bridge discovery."""
import asyncio
from os.path import abspath, dirname
from sys import path

path.insert(1, dirname(dirname(abspath(__file__))))

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


try:
    asyncio.new_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    pass

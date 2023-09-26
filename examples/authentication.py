"""AIOHue example for HUE bridge authentication."""
import argparse
import asyncio
from os.path import abspath, dirname
from sys import path

path.insert(1, dirname(dirname(abspath(__file__))))

import contextlib  # noqa: E402

from aiohue import create_app_key  # noqa: E402

parser = argparse.ArgumentParser(description="AIOHue Authentication Example")
parser.add_argument("host", help="hostname of Hue bridge")
args = parser.parse_args()


async def main():
    """Run code example."""
    host = args.host
    print()
    print("Creating app_key for bridge: ", args.host)
    print()
    # the link button must be pressed before sending the authentication request
    input("Press the link button on the bridge and press enter to continue...")

    # request api_key from bridge
    try:
        api_key = await create_app_key(host, "authentication_example")
        print()
        print("Authentication succeeded, api key: ", api_key)
        print("NOTE: store the app_key for next connections, it does not expire.")
        print()
    except Exception as exc:  # pylint: disable=broad-except
        print("ERROR: ", str(exc))
        print()


with contextlib.suppress(KeyboardInterrupt):
    asyncio.run(main())

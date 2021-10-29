"""AIOHue example for HUE bridge authentication."""
import argparse
import asyncio
import os
import sys

sys.path.insert(1, os.path.abspath(".."))

from aiohue import HueBridgeV1, HueBridgeV2, is_v2_bridge

parser = argparse.ArgumentParser(description='AIOHue Authentication Example')
parser.add_argument('host', help='hostname of Hue bridge')
args = parser.parse_args()


async def main():
    """Run code example."""
    host = args.host
    print()
    print("Connecting to bridge: ", args.host)
    print()
    # the link button must be pressed before sending the authentication request
    input("Press the link button on the bridge and press enter to continue...")

    if await is_v2_bridge(args.host):
        bridge = HueBridgeV2(host)
    else:
        bridge = HueBridgeV1(host)
    # request api_key from bridge

    try:
        api_key = await bridge.create_user("authentication_example")
        print()
        print("Authentication succeeded, api key: ", api_key)
        print("NOTE: store the app_key for next connections, it does not expire.")
        print()
    except Exception as exc: # pylint: disable=broad-except
        print("ERROR: ", str(exc))
        print()
        await bridge.close()
    else:
        # once authenticated, the bridge can be initialized
        await bridge.initialize()

try:
    asyncio.new_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    pass

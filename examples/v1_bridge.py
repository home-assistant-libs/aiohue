"""Example script for using AIOHue connecting to a V1 Hue bridge."""
import argparse
import asyncio
import logging
from os.path import abspath, dirname
from sys import path

path.insert(1, dirname(dirname(abspath(__file__))))

from aiohue import HueBridgeV1
from aiohue.v1.lights import Light

parser = argparse.ArgumentParser(description="AIOHue Example")
parser.add_argument("host", help="hostname of Hue bridge")
parser.add_argument("appkey", help="appkey for Hue bridge")
parser.add_argument("--debug", help="enable debug logging", action="store_true")
args = parser.parse_args()


async def main():
    """Run Main execution."""
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)-15s %(levelname)-5s %(name)s -- %(message)s",
        )

    async with HueBridgeV1(args.host, args.appkey) as bridge:
        print("Connected to bridge: ", bridge.bridge_id)

        print()
        print("found lights:")
        for item in bridge.lights:
            print(item)

        # turn on a light
        light: Light = bridge.lights.items[0]
        print("Turning on light", light.name)
        await light.set_state(on=True)
        await asyncio.sleep(1)

        print("Set brightness 100 to light", light.name)
        await light.set_state(bri=100, transitiontime=1000)
        await asyncio.sleep(2)

        print("Set color to light", light.name)
        await light.set_state(xy=(0.141, 0.123))
        await asyncio.sleep(1)
        print("Turning off light", light.name)
        await light.set_state(on=False)

        # V1 bridge does not support events
        # you must request updates yourself manually...
        print("requesting update of all lights")
        await bridge.lights.update()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass

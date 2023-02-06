"""Example script for using AIOHue connecting to a V2 Hue bridge."""
import argparse
import asyncio
import logging
from os.path import abspath, dirname
from sys import path

path.insert(1, dirname(dirname(abspath(__file__))))

from aiohue import HueBridgeV2

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

    async with HueBridgeV2(args.host, args.appkey) as bridge:
        print("Connected to bridge: ", bridge.bridge_id)
        print(bridge.config.bridge_device)

        print()
        print("found devices:")
        for item in bridge.devices:
            print(item.metadata.name)

        # turn on a light
        light = next(x for x in bridge.lights.items if x.supports_color)
        print("Turning on light", light.id)
        await bridge.lights.turn_on(light.id)
        await asyncio.sleep(1)
        print("Set brightness 100 to light", light.id)
        await bridge.lights.set_brightness(light.id, 100, 2000)
        await asyncio.sleep(2)
        print("Set color to light", light.id)
        await bridge.lights.set_color(light.id, 0.141, 0.123, 2000)
        await asyncio.sleep(1)
        print("Turning off light", light.id)
        await bridge.lights.turn_off(light.id, 2000)

        print()
        print("Subscribing to events...")

        def print_event(event_type, item):
            print()
            print("received event", event_type.value, item)
            print()

        bridge.subscribe(print_event)

        await asyncio.sleep(3600)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass

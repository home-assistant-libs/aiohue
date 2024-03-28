"""Example/test script for (stress) testing multiple requests to the bridge."""

import argparse
import asyncio
import contextlib
import logging
import time

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
        asyncio.get_running_loop().set_debug(True)

    async with HueBridgeV2(args.host, args.appkey) as bridge:
        print("Connected to bridge: ", bridge.bridge_id)
        print(bridge.config.bridge_device)

        # pick a random light
        light = bridge.lights.items[0]
        print(f"Sending 100 requests to bridge for {light.name}...")

        async def toggle_light():
            await bridge.lights.turn_on(light.id)
            await bridge.lights.turn_off(light.id)

        before = time.time()
        await asyncio.gather(*[toggle_light() for i in range(50)])
        after = time.time()
        print(f"Completed in {after-before} seconds...")


with contextlib.suppress(KeyboardInterrupt):
    asyncio.run(main())

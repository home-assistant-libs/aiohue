"""Example script for using AIOHue connecting to a Hue bridge."""
import asyncio
import logging
import sys
from pprint import pformat

from aiohue import HueBridgeV2
from aiohue.discovery import discover_nupnp
from aiohue.errors import LinkButtonNotPressed


async def main():
    """Run Main execution."""
    # TODO: make this a bit prettier with argparse
    app_key = None
    host = None
    if len(sys.argv) == 1:
        # if no arguments are given, discover bridge with nupnp
        discovered_bridges = await discover_nupnp()
        host = discovered_bridges[1].host
        print("Found bridge at", host)
    elif len(sys.argv) > 2:
        # both host and key are given
        host = sys.argv[1]
        app_key = sys.argv[2]
    else:
        host = sys.argv[1]

    if app_key is None:
        try:
            bridge = HueBridgeV2(host, app_key)
            app_key = await bridge.create_user("aiophue-example")
        except LinkButtonNotPressed:
            print("Press the link button on the bridge before running example.py")
            return

        print("Your username is", app_key)
        print("Now run:")
        print(" ".join(sys.argv) + f" {app_key}")
        return

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(levelname)-5s %(name)s -- %(message)s",
    )

    async with HueBridgeV2(host, app_key) as bridge:

        print()
        print("found lights:")
        for item in bridge.lights:
            print(item.metadata.name)

        print()
        print("found devices:")
        for item in bridge.devices:
            print(item.metadata.name)

        # turn on a light
        light = bridge.lights.items[0]
        print("Turning on light", light.name)
        await bridge.lights.turn_on(light.id)
        await asyncio.sleep(1)
        print("Set brightness 100 to light", light.name)
        await bridge.lights.set_brightness(light.id, 100, 2000)
        await asyncio.sleep(2)
        print("Set color to light", light.name)
        await bridge.lights.set_color(light.id, 0.141, 0.123, 2000)
        await asyncio.sleep(1)
        print("Turning off light", light.name)
        await bridge.lights.turn_off(light.id, 2000)

        def print_event(event_type, item):
            print()
            print("received event", event_type.value, item)
            print()

        bridge.events.subscribe(print_event)

        await asyncio.sleep(3600)


try:
    asyncio.new_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    pass

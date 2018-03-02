import asyncio
from pprint import pprint
import sys

from aiohue.discovery import discover_nupnp


async def main():
    bridges = await discover_nupnp()
    bridge = bridges[0]

    print('Found bridge at', bridge.host)

    if len(sys.argv) == 1:
        await bridge.create_user('aiophue-example')
        print('Your username is', bridge.username)
        print('Pass this to the example to control the bridge')
        return

    bridge.username = sys.argv[1]

    await bridge.initialize()

    print('Name', bridge.config.name)
    print('Mac', bridge.config.mac)

    print()
    print('Lights:')
    for id in bridge.lights:
        light = bridge.lights[id]
        print('{}: {}'.format(light.name, 'on' if light.state['on'] else 'off'))

    print()
    print('Groups:')
    for id in bridge.groups:
        group = bridge.groups[id]
        print('{}: {}'.format(group.name, 'on' if group.action['on'] else 'off'))

asyncio.get_event_loop().run_until_complete(main())

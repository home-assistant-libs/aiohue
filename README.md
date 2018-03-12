# Aiohue
## Asynchronous library to control Philips Hue

Requires Python 3.5 and uses asyncio and aiohttp.

```python
import asyncio
from pprint import pprint

from aiohue.discovery import discover_nupnp


async def main():
    async with aiohttp.ClientSession() as session:
        await run(session)


async def run(websession):
    bridges = await discover_nupnp(websession)

    bridge = bridges[0]
    await bridge.create_user('aiophue-example')
    print('Your username is', bridge.username)

    await bridge.initialize()

    print('Name', bridge.config.name)
    print('Mac', bridge.config.mac)

    print()
    print('Lights:')
    for id in bridge.lights:
        light = bridge.lights[id]
        print('{}: {}'.format(light.name, 'on' if light.state['on'] else 'off'))

    # Change state of a light.
    await light.set_state(on=not light.state['on'])

    print()
    print('Groups:')
    for id in bridge.groups:
        group = bridge.groups[id]
        print('{}: {}'.format(group.name, 'on' if group.action['on'] else 'off'))

    # Change state of a group.
    await group.set_action(on=not group.state['on'])


asyncio.get_event_loop().run_until_complete(main())
```

## Timeouts

Aiohue does not specify any timeouts for any requests. You will need to specify them in your own code. We recommend the `async_timeout` package:

```python
import async_timeout

with async_timeout.timeout(10):
    await bridge.initialize()
```

## Contribution guidelines

Object hierarchy and property/method names should match the Philips Hue API.

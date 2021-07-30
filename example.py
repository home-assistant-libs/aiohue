from aiohue.errors import LinkButtonNotPressed
import asyncio
import logging
import os
import sys
from datetime import datetime
from pprint import pformat

import aiohttp

from aiohue.discovery import discover_nupnp
from aiohue.groups import Group
from aiohue.lights import Light
from aiohue.sensors import (
    GenericSensor,
    TYPE_CLIP_GENERICFLAG,
    TYPE_CLIP_GENERICSTATUS,
    TYPE_CLIP_HUMIDITY,
    TYPE_CLIP_LIGHTLEVEL,
    TYPE_CLIP_OPENCLOSE,
    TYPE_CLIP_PRESENCE,
    TYPE_CLIP_SWITCH,
    TYPE_CLIP_TEMPERATURE,
    TYPE_DAYLIGHT,
    TYPE_ZGP_SWITCH,
    TYPE_ZLL_LIGHTLEVEL,
    TYPE_ZLL_PRESENCE,
    TYPE_ZLL_ROTARY,
    TYPE_ZLL_SWITCH,
    TYPE_ZLL_TEMPERATURE,
)


async def main():
    async with aiohttp.ClientSession() as session:
        await run(session)


def print_light(light):
    print("{}: {}".format(light.name, "on" if light.state["on"] else "off"))


def print_group(group):
    print("{}: {}".format(group.name, "on" if group.action["on"] else "off"))


def print_sensor(sensor):
    if sensor.type in [TYPE_CLIP_SWITCH, TYPE_ZGP_SWITCH, TYPE_ZLL_SWITCH]:
        print(
            "{}: [Button Event]: {} (last_event: {})".format(
                sensor.name, sensor.buttonevent, sensor.last_event["type"]
            )
        )
    elif sensor.type in [TYPE_ZLL_ROTARY]:
        print("{}: [Rotation Event]: {}".format(sensor.name, sensor.rotaryevent))
    elif sensor.type in [TYPE_CLIP_TEMPERATURE, TYPE_ZLL_TEMPERATURE]:
        print("{}: [Temperature]: {}".format(sensor.name, sensor.temperature))
    elif sensor.type in [TYPE_CLIP_PRESENCE, TYPE_ZLL_PRESENCE]:
        print("{}: [Presence]: {}".format(sensor.name, sensor.presence))
    elif sensor.type == TYPE_CLIP_OPENCLOSE:
        print("{}: [Open]: {}".format(sensor.name, sensor.open))
    elif sensor.type in [TYPE_CLIP_LIGHTLEVEL, TYPE_ZLL_LIGHTLEVEL]:
        print("{}: [Light Level]: {}".format(sensor.name, sensor.lightlevel))
    elif sensor.type == TYPE_CLIP_HUMIDITY:
        print("{}: [Humidity]: {}".format(sensor.name, sensor.humidity))
    elif sensor.type == TYPE_CLIP_GENERICSTATUS:
        print("{}: [Status]: {}".format(sensor.name, sensor.status))
    elif sensor.type == TYPE_CLIP_GENERICFLAG:
        print("{}: [Flag]: {}".format(sensor.name, sensor.flag))
    elif sensor.type == TYPE_DAYLIGHT:
        print("{}: [Daylight]: {}".format(sensor.name, sensor.daylight))
    else:
        print(
            "{}: [State]: {} [Config]: {}".format(
                sensor.name, sensor.state, sensor.config
            )
        )


async def run(websession):
    bridges = await discover_nupnp(websession)
    bridge = bridges[0]

    print("Found bridge at", bridge.host)

    if len(sys.argv) == 1:
        try:
            await bridge.create_user("aiophue-example")
        except LinkButtonNotPressed:
            print("Press the link button on the bridge before running example.py")
            return

        print("Your username is", bridge.username)
        print("Now run:")
        print(" ".join(sys.argv) + f" {bridge.username}")
        return

    bridge.username = sys.argv[1]

    if os.environ.get("DEBUG") == "1":
        logging.basicConfig(
            level=logging.DEBUG,
            filename="example-debug.log",
            format="%(asctime)s %(message)s",
            datefmt="%H:%M:%S",
        )

    logger = logging.getLogger(__name__)

    await bridge.initialize()

    print("Name", bridge.config.name)
    print("Mac", bridge.config.mac)
    print("API version", bridge.config.apiversion)

    print()
    print("Lights:")
    for id in bridge.lights:
        light = bridge.lights[id]
        print_light(light)
        logger.debug("light %s: %s", light.id, pformat(light.state))

    print()
    print("Groups:")
    for id in bridge.groups:
        group = bridge.groups[id]
        print_group(group)
        logger.debug("group %s: %s %s", group.id, group.state, pformat(group.action))

    print()
    print("Scenes:")
    for id in bridge.scenes:
        scene = bridge.scenes[id]
        print(scene.name)

    print()
    print("Sensors:")
    for id in bridge.sensors:
        sensor = bridge.sensors[id]
        print_sensor(sensor)
        logger.debug(
            "sensor %s (%s): %s", sensor.id, sensor.type, pformat(sensor.state)
        )

    print()
    print("Listening for events")
    print()

    try:
        async for updated_object in bridge.listen_events():
            print(datetime.now().strftime("%H:%M:%S"), end=" ")
            if isinstance(updated_object, Group):
                print("Group: ", end="")
                print_group(updated_object)
            elif isinstance(updated_object, Light):
                print("Light: ", end="")
                print_light(updated_object)
            elif isinstance(updated_object, GenericSensor):
                print("Sensor: ", end="")
                print_sensor(updated_object)
            else:
                print("{}: {}".format(type(updated_object).__name__, updated_object))
    except GeneratorExit:
        pass


try:
    asyncio.get_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    pass

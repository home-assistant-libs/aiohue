"""Example script for using AIOHue connecting to a V2 Hue bridge."""

import argparse
import asyncio
import contextlib
import logging
import random

from aiohue import HueBridgeV2
from aiohue.v2.models.speaker_feature import SupportedSound

parser = argparse.ArgumentParser(description="AIOHue Example")
parser.add_argument("host", help="hostname of Hue bridge")
parser.add_argument("appkey", help="appkey for Hue bridge")
parser.add_argument("--debug", help="enable debug logging", action="store_true")
args = parser.parse_args()


def select_supported_sound(sounds) -> SupportedSound | None:
    """Pick a sound to play from a list of supported sounds."""
    # a sound this version of aiohue does not know yet parses as UNKNOWN,
    # which the bridge would reject if we sent it back
    skip = (SupportedSound.NO_SOUND, SupportedSound.UNKNOWN)
    playable = [x for x in sounds if x not in skip]
    return random.choice(playable) if playable else None


async def play_and_wait(bridge, speaker, play_request):
    """
    Play a sound and wait until the speaker reports itself idle again.

    The bridge clears the played sound a fair bit after the audio has finished,
    so this returns later than the sound is actually audible.
    """
    done = asyncio.Event()
    started = False

    def on_update(_event_type, item):
        nonlocal started
        if item.is_playing_sound:
            started = True
        elif started:
            done.set()

    # subscribe before sending the request, so the state change cannot be missed
    unsubscribe = bridge.speakers.subscribe(on_update, id_filter=speaker.id)
    try:
        await play_request
        await done.wait()
    finally:
        unsubscribe()


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

        # speaker interaction examples
        speaker = next(iter(bridge.speakers), None)
        if speaker is not None:
            if sound := select_supported_sound(speaker.supported_chime_sounds):
                print("Playing chime sound <", sound, "> on speaker", speaker.id)
                await play_and_wait(
                    bridge,
                    speaker,
                    bridge.speakers.play_chime(speaker.id, sound, volume=50),
                )
            if sound := select_supported_sound(speaker.supported_alert_sounds):
                print("Playing alert sound <", sound, "> on speaker", speaker.id)
                await play_and_wait(
                    bridge,
                    speaker,
                    bridge.speakers.play_alert(speaker.id, sound, volume=50),
                )

        print("waiting for events...")
        await asyncio.sleep(3600)


with contextlib.suppress(KeyboardInterrupt):
    asyncio.run(main())

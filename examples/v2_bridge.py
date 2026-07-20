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


def select_supported_sound(sounds) -> SupportedSound:
    """Choose a viable sound given a list of supported sounds, helper for speaker examples."""
    sound = random.choice(sounds)
    while sound == SupportedSound.NO_SOUND:
        sound = random.choice(sounds)
    return sound


class YeildToEventLoop:
    """Yield to the event loop, for speaker examples."""

    def __await__(self):
        """Give control to the event loop on await."""
        yield


async def check_speaker_is_playing(event, speaker):
    """Check speaker playing state until speaker is done playing sound, for speaker examples."""
    while True:
        if not speaker.is_playing_sound:
            event.set()
            break
        await YeildToEventLoop()


async def until_speaker_sound_end(speaker):
    """Wait until the speaker is done playing the current sound, helper for speaker examples."""
    event = asyncio.Event()
    await asyncio.sleep(2)
    task = asyncio.create_task(check_speaker_is_playing(event, speaker))
    await event.wait()
    await task


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
        speaker = next(x for x in bridge.speakers.items)
        if speaker.supports_alarm:
            sound = select_supported_sound(speaker.supported_alarm_sounds)
            print("Playing alarm sound <", sound, "> on speaker", speaker.id)
            await bridge.speakers.play_alarm(
                speaker.id, sound, volume=50, duration=1000
            )
            await until_speaker_sound_end(speaker)
        if speaker.supports_chime:
            sound = select_supported_sound(speaker.supported_chime_sounds)
            print("Playing chime sound <", sound, "> on speaker", speaker.id)
            await bridge.speakers.play_chime(speaker.id, sound, volume=50)
            await until_speaker_sound_end(speaker)
        if speaker.supports_alert:
            sound = select_supported_sound(speaker.supported_alert_sounds)
            print("Playing alert sound <", sound, "> on speaker", speaker.id)
            await bridge.speakers.play_alert(speaker.id, sound, volume=50)
            await until_speaker_sound_end(speaker)

        print("sounds done playing, now waiting for other events...")
        await asyncio.sleep(3600)


with contextlib.suppress(KeyboardInterrupt):
    asyncio.run(main())

"""Test speakers controller functions."""

import datetime
from unittest.mock import patch

from aiohue import HueBridgeV2
from aiohue.v2 import EventType
from aiohue.v2.models.speaker_feature import MuteStatus, SupportedSound

SPEAKER_ID = "3903d908-eb6c-8ece-335c-f7ae230943f0"


async def bridge_with_speaker(v2_resources) -> HueBridgeV2:
    """Return a bridge with the fixture state loaded."""
    bridge = HueBridgeV2("127.0.0.1", "fake")
    with patch.object(bridge, "request", return_value=v2_resources):
        await bridge.fetch_full_state()
    return bridge


async def test_speaker_parsed_from_fixture(v2_resources):
    """Ensure the speaker resource and its sound features are parsed."""
    bridge = await bridge_with_speaker(v2_resources)
    speaker = bridge.speakers[SPEAKER_ID]

    assert speaker.supports_alarm
    assert speaker.supports_chime
    assert speaker.supports_alert
    assert SupportedSound.SIREN in speaker.supported_alarm_sounds
    assert not speaker.is_playing_sound
    assert not speaker.is_muted


async def test_play_chime_request_body(v2_resources):
    """Ensure a chime request carries the sound and volume."""
    bridge = await bridge_with_speaker(v2_resources)

    with patch.object(bridge, "request", return_value=[]) as request:
        await bridge.speakers.play_chime(
            SPEAKER_ID, SupportedSound.DING_DONG_CLASSIC, volume=50
        )

    assert request.call_args.args[1] == f"clip/v2/resource/speaker/{SPEAKER_ID}"
    assert request.call_args.kwargs["json"] == {
        "chime": {"sound": "ding_dong_classic", "volume": {"level": 50}}
    }


async def test_play_alarm_sends_duration(v2_resources):
    """Ensure duration is sent for the alarm, the only feature that accepts it."""
    bridge = await bridge_with_speaker(v2_resources)

    with patch.object(bridge, "request", return_value=[]) as request:
        await bridge.speakers.play_alarm(
            SPEAKER_ID, SupportedSound.SIREN, volume=100, duration=5000
        )

    assert request.call_args.kwargs["json"] == {
        "alarm": {"sound": "siren", "volume": {"level": 100}, "duration": 5000}
    }


async def test_play_alert_request_body(v2_resources):
    """Ensure an alert request carries the sound and volume but no duration."""
    bridge = await bridge_with_speaker(v2_resources)

    with patch.object(bridge, "request", return_value=[]) as request:
        await bridge.speakers.play_alert(SPEAKER_ID, SupportedSound.ALERT, volume=70)

    assert request.call_args.kwargs["json"] == {
        "alert": {"sound": "alert", "volume": {"level": 70}}
    }


async def test_set_mute_request_body(v2_resources):
    """Ensure muting sends the mute feature."""
    bridge = await bridge_with_speaker(v2_resources)

    with patch.object(bridge, "request", return_value=[]) as request:
        await bridge.speakers.set_mute(SPEAKER_ID, MuteStatus.MUTE)

    assert request.call_args.kwargs["json"] == {"mute": {"mute": "mute"}}


async def test_playing_alarm_reports_estimated_end(v2_resources):
    """Ensure a playing siren exposes its estimated end time."""
    bridge = await bridge_with_speaker(v2_resources)

    # shape captured from a live chime while the siren was playing
    # pylint: disable=protected-access
    await bridge.speakers._handle_event(
        EventType.RESOURCE_UPDATED,
        {
            "id": SPEAKER_ID,
            "type": "speaker",
            "alarm": {
                "sound_values": ["siren", "no_sound"],
                "status": {
                    "sound": "siren",
                    "sound_values": ["siren", "no_sound"],
                    "estimated_end": {"estimate": "2026-07-27T21:25:46.056Z"},
                },
            },
        },
    )

    speaker = bridge.speakers[SPEAKER_ID]
    assert speaker.is_playing_alarm
    assert speaker.is_playing_sound
    assert speaker.alarm.status.estimated_end.estimate == datetime.datetime(
        2026, 7, 27, 21, 25, 46, 56000, tzinfo=datetime.UTC
    )


async def test_unknown_sound_does_not_break_parsing(v2_resources):
    """Ensure a sound value we don't know yet degrades instead of raising."""
    bridge = await bridge_with_speaker(v2_resources)

    assert SupportedSound("something_new") == SupportedSound.UNKNOWN
    assert bridge.speakers[SPEAKER_ID] is not None

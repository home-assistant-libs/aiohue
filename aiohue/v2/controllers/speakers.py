"""Controller holding and managing HUE resources of type `speaker`."""

from aiohue.v2.models.resource import ResourceTypes
from aiohue.v2.models.speaker import Speaker, SpeakerPut
from aiohue.v2.models.speaker_feature import (
    MuteFeature,
    MuteStatus,
    SoundFeaturePut,
    SupportedSound,
    VolumeFeature,
)

from .base import BaseResourcesController


class SpeakersController(BaseResourcesController[type[Speaker]]):
    """Controller holding and managing HUE resources of type `speaker`."""

    item_type = ResourceTypes.SPEAKER
    item_cls = Speaker

    async def play_alarm(
        self,
        id: str,
        sound: SupportedSound,
        volume: int | None = None,
        duration: int | None = None,
    ) -> None:
        """
        Play an alarm sound on the speaker.

        The alarm is the only sound feature that accepts a duration, given in
        milliseconds and rounded up to the next multiple of 1000.
        """
        await self.__set_state(id, alarm=_sound_feature_put(sound, volume, duration))

    async def play_chime(
        self,
        id: str,
        sound: SupportedSound,
        volume: int | None = None,
    ) -> None:
        """Play a chime sound on the speaker."""
        await self.__set_state(id, chime=_sound_feature_put(sound, volume))

    async def play_alert(
        self,
        id: str,
        sound: SupportedSound,
        volume: int | None = None,
    ) -> None:
        """Play an alert sound on the speaker."""
        await self.__set_state(id, alert=_sound_feature_put(sound, volume))

    async def set_mute(
        self,
        id: str,
        mute: MuteStatus,
    ) -> None:
        """
        Mute or unmute the speaker.

        A speaker has a single global mute state. The alarm is not affected by it.
        """
        await self.__set_state(id, mute=mute)

    async def __set_state(
        self,
        id: str,
        alarm: SoundFeaturePut | None = None,
        chime: SoundFeaturePut | None = None,
        alert: SoundFeaturePut | None = None,
        mute: MuteStatus | None = None,
    ) -> None:
        """Set supported feature(s) to speaker resource."""
        update_obj = SpeakerPut(alarm=alarm, chime=chime, alert=alert)
        if mute is not None:
            update_obj.mute = MuteFeature(mute=mute)
        await self.update(id, update_obj)


def _sound_feature_put(
    sound: SupportedSound, volume: int | None = None, duration: int | None = None
) -> SoundFeaturePut:
    """Build the request body for a play-sound request."""
    update_obj = SoundFeaturePut(sound=sound, duration=duration)
    if volume is not None:
        update_obj.volume = VolumeFeature(level=volume)
    return update_obj

"""Controller holding and managing HUE resources of type `speaker`."""

from aiohue.v2.models.speaker import Speaker, SpeakerPut
from aiohue.v2.models.speaker_feature import (
    MuteStatus,
    MuteFeature,
    SupportedSound,
    SoundFeaturePut,
    VolumeFeature,
)
from aiohue.v2.models.resource import ResourceTypes

from .base import BaseResourcesController


def _get_sound_feature_put(
    sound: SupportedSound, volume: int | None = None, duration: int | None = None
) -> SoundFeaturePut | None:
    update_obj = SoundFeaturePut(sound=sound, duration=duration)
    if volume is not None:
        update_obj.volume = VolumeFeature(level=volume)
    return update_obj


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
        """Set alarm sound of speaker resource."""
        await self.__set_state(
            id, alarm=_get_sound_feature_put(sound, volume, duration)
        )

    async def play_chime(
        self,
        id: str,
        sound: SupportedSound,
        volume: int | None = None,
    ) -> None:
        """Set chime sound of speaker resource."""
        await self.__set_state(id, chime=_get_sound_feature_put(sound, volume))

    async def play_alert(
        self,
        id: str,
        sound: SupportedSound,
        volume: int | None = None,
    ) -> None:
        """Set alert sound of speaker resource."""
        await self.__set_state(id, alert=_get_sound_feature_put(sound, volume))

    async def set_mute(
        self,
        id: str,
        mute: MuteStatus,
    ) -> None:
        """Set mute state of speaker resource."""
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
        await self.update(
            id,
            update_obj,
        )

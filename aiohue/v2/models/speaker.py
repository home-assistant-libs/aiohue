"""
Model(s) for Speaker resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_speaker
"""

from dataclasses import dataclass

from .speaker_feature import (
    MuteStatus,
    SupportedSound,
    MuteFeature,
    SoundFeature,
    SoundFeaturePut,
)
from .resource import ResourceIdentifier, ResourceTypes


@dataclass
class Speaker:
    """
    Represent a Speaker resource when retrieved from the HUE api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_speaker_get
    """

    # id: required(string)
    id: str
    # owner: required(ResourceIdentifier)
    owner: ResourceIdentifier

    # type: required(ResourceTypes)
    type: ResourceTypes = ResourceTypes.SPEAKER

    # id_v1: string
    id_v1: str | None = None
    # alarm: SoundFeature
    alarm: SoundFeature | None = None
    # chime: SoundsFeature
    chime: SoundFeature | None = None
    # alert: SoundFeature
    alert: SoundFeature | None = None
    # mute: MuteFeature
    mute: MuteFeature | None = None

    @property
    def supports_alarm(self) -> bool:
        """Return if this speaker supports alarm sound feature."""
        return self.alarm is not None

    @property
    def supported_alarm_sounds(self) -> list[SupportedSound]:
        """Return list of supported alarm sounds."""
        return self.alarm.sound_values if self.alarm else []

    @property
    def is_playing_alarm(self) -> bool:
        """Return true if speaker is currently playing an alarm sound, false if not."""
        if self.alarm is not None:
            return self.alarm.status.sound != SupportedSound.NO_SOUND
        return False

    @property
    def supports_chime(self) -> bool:
        """Return if this speaker supports chime sound feature."""
        return self.chime is not None

    @property
    def supported_chime_sounds(self) -> list[SupportedSound]:
        """Return list of supported chime sounds."""
        return self.chime.sound_values if self.chime else []

    @property
    def is_playing_chime(self) -> bool:
        """Return true if speaker is currently playing a chime sound, false if not."""
        if self.chime is not None:
            return self.chime.status.sound != SupportedSound.NO_SOUND
        return False

    @property
    def supports_alert(self) -> bool:
        """Return if this speaker supports alert sound feature."""
        return self.alert is not None

    @property
    def supported_alert_sounds(self) -> list[SupportedSound]:
        """Return list of supported alert sounds."""
        return self.alert.sound_values if self.alert else []

    @property
    def is_playing_alert(self) -> bool:
        """Return true if speaker is currently playing an alert sound, false if not."""
        if self.alert is not None:
            return self.alert.status.sound != SupportedSound.NO_SOUND
        return False

    @property
    def is_playing_sound(self) -> bool:
        """Return true if speaker is currently playing any sound, false if not."""
        return self.is_playing_alarm or self.is_playing_chime or self.is_playing_alert

    @property
    def is_muted(self) -> bool:
        """Return true if speaker is currently muted, false if not muted."""
        if self.mute is not None:
            return self.mute.mute == MuteStatus.MUTE
        return False


@dataclass
class SpeakerPut:
    """
    Speaker resource properties that can be set/updated with a PUT request to the HUE api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_speaker_put
    """

    # alarm: SoundFeature
    alarm: SoundFeaturePut | None = None
    # chime: SoundsFeature
    chime: SoundFeaturePut | None = None
    # alert: SoundFeature
    alert: SoundFeaturePut | None = None
    # mute: MuteFeature
    mute: MuteFeature | None = None

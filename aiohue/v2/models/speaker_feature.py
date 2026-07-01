"""Speaker Feature schemas used by Hue speaker resources."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class MuteStatus(StrEnum):
    """Enum with possible mute statuses."""

    MUTE = "mute"
    UNMUTE = "unmute"


@dataclass
class MuteFeature:
    """
    Represents the MuteFeature of a speaker resource.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_speaker_get
    """

    # mute: required(one of mute, unmute)
    # A speaker devices has a global mute status. This will not affect the siren
    mute: MuteStatus


@dataclass
class EstimatedEndFeature:
    """
    Represents the EstimatedEndFeature of a speaker resource.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_speaker_get
    """

    # estimate: required(datetime)
    estimate: datetime


class SupportedSound(StrEnum):
    """Enum of possible sounds."""

    NO_SOUND = "no_sound"
    ALERT = "alert"
    BLEEP = "bleep"
    DING_DONG_CLASSIC = "ding_dong_classic"
    DING_DONG_MODERN = "ding_dong_modern"
    RISE = "rise"
    SIREN = "siren"
    WESTMINSTER_CLASSIC = "westminster_classic"
    WESTMINSTER_MODERN = "westminster_modern"
    DING_DONG_XYLO = "ding_dong_xylo"
    HUE_DEFAULT = "hue_default"
    SONAR = "sonar"
    SWING = "swing"
    BRIGHT = "bright"
    GLOW = "glow"
    BOUNCE = "bounce"
    REVEAL = "reveal"
    WELCOME = "welcome"
    BRIGHT_MODERN = "bright_modern"
    FAIRY = "fairy"
    GALAXY = "galaxy"
    ECHO = "echo"


@dataclass
class SoundStatusBase:
    """
    Represents the base SoundStatus base properties.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_speaker_get
    """

    # sound: required(one of Sound)
    sound: SupportedSound


@dataclass
class SoundStatus(SoundStatusBase):
    """
    Represents the SoundStatus of a speaker resource.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_speaker_get
    """

    # sound_values: required(array of supported Sound, minItems: 2)
    sound_values: list[SupportedSound]
    # estimated_end: only present for siren sound
    # Estimated end-time of the current sound based on duration.
    estimated_end: EstimatedEndFeature | None


@dataclass
class VolumeFeature:
    """
    Represents the Volume Feature of a speaker resource when updating/sending in PUT requests.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_speaker_get
    """

    # level: required(int, minimum: 0, maximum: 100)
    level: int


@dataclass
class SoundFeaturePut(SoundStatusBase):
    """
    Represents the SoundStatus properties that can be set/updated with a PUT request to the HUE api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_speaker_put
    """

    volume: VolumeFeature | None = None
    # duration: int, minimum: 0, maximum: 65534000
    # Only applicable for alert sound feature
    # Stepsize of 1000ms, values in between a step will be rounded up to next multiple of 1000ms.
    duration: int | None = None


@dataclass
class SoundFeature:
    """
    Represents the MuteFeature of a speaker resource.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_speaker_get
    """

    # sound_values: required(array of supported Sound, minItems: 1)
    sound_values: list[SupportedSound]
    # status: required(one of SoundStatus)
    status: SoundStatus

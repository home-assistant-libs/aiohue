"""Models for execution, hdmi, and hue resources on the Hue Sync Box."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

@dataclass
class VideoSettings:
    """Settings shared by video and game sync modes."""

    intensity: str = "moderate"
    backgroundLighting: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> "VideoSettings":
        return cls(
            intensity=data.get("intensity", "moderate"),
            backgroundLighting=data.get("backgroundLighting", True),
        )


@dataclass
class MusicSettings:
    """Settings for music sync mode."""

    intensity: str = "moderate"
    palette: str = "happyEnergetic"

    @classmethod
    def from_dict(cls, data: dict) -> "MusicSettings":
        return cls(
            intensity=data.get("intensity", "moderate"),
            palette=data.get("palette", "happyEnergetic"),
        )


@dataclass
class ExecutionResource:
    """
    Full state of the /api/v1/execution resource.

    Controls the current sync mode, source, brightness, and per-mode settings.
    """

    mode: str = "powersave"
    syncActive: bool = False
    hdmiActive: bool = False
    hdmiSource: str = "input1"
    hueTarget: str = ""
    brightness: int = 100
    lastSyncMode: str = "video"
    video: VideoSettings = field(default_factory=VideoSettings)
    game: VideoSettings = field(default_factory=VideoSettings)
    music: MusicSettings = field(default_factory=MusicSettings)
    preset: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionResource":
        return cls(
            mode=data.get("mode", "powersave"),
            syncActive=data.get("syncActive", False),
            hdmiActive=data.get("hdmiActive", False),
            hdmiSource=data.get("hdmiSource", "input1"),
            hueTarget=data.get("hueTarget", ""),
            brightness=data.get("brightness", 100),
            lastSyncMode=data.get("lastSyncMode", "video"),
            video=VideoSettings.from_dict(data.get("video", {})),
            game=VideoSettings.from_dict(data.get("game", {})),
            music=MusicSettings.from_dict(data.get("music", {})),
            preset=data.get("preset"),
        )


# ---------------------------------------------------------------------------
# HDMI
# ---------------------------------------------------------------------------

@dataclass
class HdmiPort:
    """State of a single HDMI port (input1–input4 or output)."""

    name: str = ""
    type: str = "generic"
    status: str = "unknown"
    lastSyncMode: str = "video"

    @classmethod
    def from_dict(cls, data: dict) -> "HdmiPort":
        return cls(
            name=data.get("name", ""),
            type=data.get("type", "generic"),
            status=data.get("status", "unknown"),
            lastSyncMode=data.get("lastSyncMode", "video"),
        )


@dataclass
class HdmiResource:
    """Full state of the /api/v1/hdmi resource."""

    input1: HdmiPort = field(default_factory=HdmiPort)
    input2: HdmiPort = field(default_factory=HdmiPort)
    input3: HdmiPort = field(default_factory=HdmiPort)
    input4: HdmiPort = field(default_factory=HdmiPort)
    output: HdmiPort = field(default_factory=HdmiPort)
    contentSpecs: str = ""
    videoSyncSupported: bool = False
    audioSyncSupported: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "HdmiResource":
        return cls(
            input1=HdmiPort.from_dict(data.get("input1", {})),
            input2=HdmiPort.from_dict(data.get("input2", {})),
            input3=HdmiPort.from_dict(data.get("input3", {})),
            input4=HdmiPort.from_dict(data.get("input4", {})),
            output=HdmiPort.from_dict(data.get("output", {})),
            contentSpecs=data.get("contentSpecs", ""),
            videoSyncSupported=data.get("videoSyncSupported", False),
            audioSyncSupported=data.get("audioSyncSupported", False),
        )


# ---------------------------------------------------------------------------
# Hue bridge connection
# ---------------------------------------------------------------------------

@dataclass
class HueGroup:
    """An entertainment area/group on the paired Hue bridge."""

    name: str = ""
    numLights: int = 0
    active: bool = False
    owner: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "HueGroup":
        return cls(
            name=data.get("name", ""),
            numLights=data.get("numLights", 0),
            active=data.get("active", False),
            owner=data.get("owner"),
        )


@dataclass
class HueResource:
    """Full state of the /api/v1/hue resource."""

    bridgeUniqueId: str = ""
    bridgeIpAddress: str = ""
    connectionState: str = "uninitialized"
    groups: dict[str, HueGroup] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "HueResource":
        groups = {
            gid: HueGroup.from_dict(gdata)
            for gid, gdata in data.get("groups", {}).items()
        }
        return cls(
            bridgeUniqueId=data.get("bridgeUniqueId", ""),
            bridgeIpAddress=data.get("bridgeIpAddress", ""),
            connectionState=data.get("connectionState", "uninitialized"),
            groups=groups,
        )

"""Models for the Hue Sync Box API."""
from .behavior import BehaviorResource, InputBehavior, IrCode, IrResource, IrScan, Preset, Registration
from .device import Capabilities, DeviceResource, UpdateConfig, WifiInfo
from .execution import (
    ExecutionResource,
    HdmiPort,
    HdmiResource,
    HueGroup,
    HueResource,
    MusicSettings,
    VideoSettings,
)

__all__ = [
    "BehaviorResource",
    "Capabilities",
    "DeviceResource",
    "ExecutionResource",
    "HdmiPort",
    "HdmiResource",
    "HueGroup",
    "HueResource",
    "InputBehavior",
    "IrCode",
    "IrResource",
    "IrScan",
    "MusicSettings",
    "Preset",
    "Registration",
    "UpdateConfig",
    "VideoSettings",
    "WifiInfo",
]

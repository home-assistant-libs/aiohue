"""Models for the /device resource on the Hue Sync Box."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WifiInfo:
    """Wifi connection information."""

    ssid: str = ""
    # 0=not connected, 1=weak, 2=fair, 3=good, 4=excellent
    strength: int = 0


@dataclass
class UpdateConfig:
    """Automatic firmware update configuration."""

    autoUpdateEnabled: bool = True
    # UTC hour (0-23) when auto-update runs
    autoUpdateTime: int = 10


@dataclass
class Capabilities:
    """Device capability limits."""

    maxIrCodes: int = 0
    maxPresets: int = 0


@dataclass
class DeviceResource:
    """
    Full state of the /api/v1/device resource.

    Only GET on /api/v1/device is available without an access token.
    Writable fields: name, ledMode, action, update/*, bluetooth.
    """

    name: str = ""
    deviceType: str = ""
    uniqueId: str = ""
    apiLevel: int = 0
    firmwareVersion: str = ""
    buildNumber: int = 0
    wifiState: str = "uninitialized"
    ipAddress: str = ""
    wifi: WifiInfo = field(default_factory=WifiInfo)
    ledMode: int = 1
    action: str = "none"
    update: UpdateConfig = field(default_factory=UpdateConfig)
    capabilities: Capabilities = field(default_factory=Capabilities)
    updatableFirmwareVersion: Optional[str] = None
    updatableBuildNumber: Optional[int] = None
    lastCheckedUpdate: Optional[str] = None
    overheating: bool = False
    undervolt: bool = False
    # Sync Box 8K only
    bluetooth: Optional[bool] = None
    # apiLevel 10+
    beta: Optional[bool] = None
    termsAgreed: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict) -> "DeviceResource":
        wifi = WifiInfo(**data.get("wifi", {}))
        update_raw = data.get("update", {})
        update = UpdateConfig(**update_raw) if update_raw else UpdateConfig()
        caps_raw = data.get("capabilities", {})
        caps = Capabilities(**caps_raw) if caps_raw else Capabilities()
        return cls(
            name=data.get("name", ""),
            deviceType=data.get("deviceType", ""),
            uniqueId=data.get("uniqueId", ""),
            apiLevel=data.get("apiLevel", 0),
            firmwareVersion=data.get("firmwareVersion", ""),
            buildNumber=data.get("buildNumber", 0),
            wifiState=data.get("wifiState", "uninitialized"),
            ipAddress=data.get("ipAddress", ""),
            wifi=wifi,
            ledMode=data.get("ledMode", 1),
            action=data.get("action", "none"),
            update=update,
            capabilities=caps,
            updatableFirmwareVersion=data.get("updatableFirmwareVersion"),
            updatableBuildNumber=data.get("updatableBuildNumber"),
            lastCheckedUpdate=data.get("lastCheckedUpdate"),
            overheating=data.get("overheating", False),
            undervolt=data.get("undervolt", False),
            bluetooth=data.get("bluetooth"),
            beta=data.get("beta"),
            termsAgreed=data.get("termsAgreed"),
        )

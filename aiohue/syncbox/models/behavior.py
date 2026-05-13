"""Models for behavior, IR, registrations, and presets resources."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Behavior
# ---------------------------------------------------------------------------

@dataclass
class InputBehavior:
    """Per-input behavior settings (Sync Box 4K)."""

    cecInputSwitch: int = 1
    linkAutoSync: int = 0
    hdrMode: int = 0
    # 4K only
    hpdInputPortSwitch: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "InputBehavior":
        return cls(
            cecInputSwitch=data.get("cecInputSwitch", 1),
            linkAutoSync=data.get("linkAutoSync", 0),
            hdrMode=data.get("hdrMode", 0),
            hpdInputPortSwitch=data.get("hpdInputPortSwitch"),
        )


@dataclass
class BehaviorResource:
    """Full state of the /api/v1/behavior resource."""

    inactivePowersave: int = 20
    cecPowersave: int = 1
    usbPowersave: int = 1
    hpdInputSwitch: int = 1
    hpdOutputEnableMs: int = 1500
    arcBypassMode: int = 0
    forceDoviNative: int = 0
    input1: InputBehavior = field(default_factory=InputBehavior)
    input2: InputBehavior = field(default_factory=InputBehavior)
    input3: InputBehavior = field(default_factory=InputBehavior)
    input4: InputBehavior = field(default_factory=InputBehavior)

    @classmethod
    def from_dict(cls, data: dict) -> "BehaviorResource":
        return cls(
            inactivePowersave=data.get("inactivePowersave", 20),
            cecPowersave=data.get("cecPowersave", 1),
            usbPowersave=data.get("usbPowersave", 1),
            hpdInputSwitch=data.get("hpdInputSwitch", 1),
            hpdOutputEnableMs=data.get("hpdOutputEnableMs", 1500),
            arcBypassMode=data.get("arcBypassMode", 0),
            forceDoviNative=data.get("forceDoviNative", 0),
            input1=InputBehavior.from_dict(data.get("input1", {})),
            input2=InputBehavior.from_dict(data.get("input2", {})),
            input3=InputBehavior.from_dict(data.get("input3", {})),
            input4=InputBehavior.from_dict(data.get("input4", {})),
        )


# ---------------------------------------------------------------------------
# IR
# ---------------------------------------------------------------------------

@dataclass
class IrScan:
    """Current IR scan state."""

    scanning: bool = False
    code: Optional[str] = None
    codes: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "IrScan":
        return cls(
            scanning=data.get("scanning", False),
            code=data.get("code"),
            codes=data.get("codes", []),
        )


@dataclass
class IrCode:
    """A single mapped IR code."""

    name: str = ""
    # execution sub-object (single key-value)
    execution: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "IrCode":
        return cls(
            name=data.get("name", ""),
            execution=data.get("execution", {}),
        )


@dataclass
class IrResource:
    """Full state of the /api/v1/ir resource."""

    defaultCodes: bool = True
    scan: IrScan = field(default_factory=IrScan)
    codes: dict[str, IrCode] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "IrResource":
        codes = {
            code_id: IrCode.from_dict(code_data)
            for code_id, code_data in data.get("codes", {}).items()
        }
        return cls(
            defaultCodes=data.get("defaultCodes", True),
            scan=IrScan.from_dict(data.get("scan", {})),
            codes=codes,
        )


# ---------------------------------------------------------------------------
# Registrations
# ---------------------------------------------------------------------------

@dataclass
class Registration:
    """A single registered API client."""

    appName: str = ""
    instanceName: str = ""
    role: str = "user"
    created: str = ""
    lastUsed: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Registration":
        return cls(
            appName=data.get("appName", ""),
            instanceName=data.get("instanceName", ""),
            role=data.get("role", "user"),
            created=data.get("created", ""),
            lastUsed=data.get("lastUsed", ""),
        )


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

@dataclass
class Preset:
    """A stored execution preset."""

    name: str = ""
    lastUsed: Optional[str] = None
    execution: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Preset":
        return cls(
            name=data.get("name", ""),
            lastUsed=data.get("lastUsed"),
            execution=data.get("execution", {}),
        )

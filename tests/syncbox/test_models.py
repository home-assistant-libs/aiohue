"""Test parsing of syncbox models."""
from aiohue.syncbox.models import (
    BehaviorResource,
    DeviceResource,
    ExecutionResource,
    HdmiResource,
    HueResource,
    IrResource,
    Registration,
)


def test_device_parsing(syncbox_state):
    """Ensure device fields are parsed correctly."""
    device = DeviceResource.from_dict(syncbox_state["device"])

    assert device.name == "My Sync Box"
    assert device.deviceType == "HSB1"
    assert device.uniqueId == "C42996000000"
    assert device.apiLevel == 7
    assert device.firmwareVersion == "1.7.4"
    assert device.buildNumber == 681947148
    assert device.wifiState == "wan"
    assert device.ipAddress == "192.168.1.12"
    assert device.ledMode == 1
    assert device.action == "none"
    assert device.updatableFirmwareVersion is None
    assert device.updatableBuildNumber is None


def test_device_wifi_parsing(syncbox_state):
    """Ensure wifi sub-object is parsed correctly."""
    device = DeviceResource.from_dict(syncbox_state["device"])

    assert device.wifi.ssid == "Wifi_2G"
    assert device.wifi.strength == 4


def test_device_update_parsing(syncbox_state):
    """Ensure update config sub-object is parsed correctly."""
    device = DeviceResource.from_dict(syncbox_state["device"])

    assert device.update.autoUpdateEnabled is True
    assert device.update.autoUpdateTime == 11


def test_device_capabilities_parsing(syncbox_state):
    """Ensure capabilities sub-object is parsed correctly."""
    device = DeviceResource.from_dict(syncbox_state["device"])

    assert device.capabilities.maxIrCodes == 24
    assert device.capabilities.maxPresets == 16


def test_execution_parsing(syncbox_state):
    """Ensure execution fields are parsed correctly."""
    execution = ExecutionResource.from_dict(syncbox_state["execution"])

    assert execution.mode == "powersave"
    assert execution.syncActive is False
    assert execution.hdmiActive is False
    assert execution.hdmiSource == "input1"
    assert execution.hueTarget == "db7dd240-d061-48bf-84c2-01f086e4bfae"
    assert execution.brightness == 122
    assert execution.lastSyncMode == "video"
    assert execution.preset is None


def test_execution_video_parsing(syncbox_state):
    """Ensure video mode settings are parsed correctly."""
    execution = ExecutionResource.from_dict(syncbox_state["execution"])

    assert execution.video.intensity == "moderate"
    assert execution.video.backgroundLighting is True


def test_execution_game_parsing(syncbox_state):
    """Ensure game mode settings are parsed correctly."""
    execution = ExecutionResource.from_dict(syncbox_state["execution"])

    assert execution.game.intensity == "high"
    assert execution.game.backgroundLighting is False


def test_execution_music_parsing(syncbox_state):
    """Ensure music mode settings are parsed correctly."""
    execution = ExecutionResource.from_dict(syncbox_state["execution"])

    assert execution.music.intensity == "high"
    assert execution.music.palette == "melancholicEnergetic"


def test_hdmi_ports_parsing(syncbox_state):
    """Ensure all HDMI ports are parsed correctly."""
    hdmi = HdmiResource.from_dict(syncbox_state["hdmi"])

    assert hdmi.input1.name == "HDMI 1"
    assert hdmi.input1.type == "generic"
    assert hdmi.input1.status == "plugged"
    assert hdmi.input1.lastSyncMode == "video"

    assert hdmi.input2.name == "Gaming"
    assert hdmi.input2.type == "xbox"
    assert hdmi.input2.status == "plugged"

    assert hdmi.input3.status == "unplugged"

    assert hdmi.input4.name == "Shield"
    assert hdmi.input4.type == "shield"

    assert hdmi.output.name == "HDMI Out"
    assert hdmi.output.status == "plugged"


def test_hdmi_content_specs_parsing(syncbox_state):
    """Ensure content specs and sync support flags are parsed correctly."""
    hdmi = HdmiResource.from_dict(syncbox_state["hdmi"])

    assert hdmi.contentSpecs == "3840 x 2160 @ 60000 - SDR"
    assert hdmi.videoSyncSupported is True
    assert hdmi.audioSyncSupported is True


def test_hue_parsing(syncbox_state):
    """Ensure hue bridge connection fields are parsed correctly."""
    hue = HueResource.from_dict(syncbox_state["hue"])

    assert hue.bridgeUniqueId == "001788FFFE000000"
    assert hue.bridgeIpAddress == "192.168.1.8"
    assert hue.connectionState == "connected"


def test_hue_groups_parsing(syncbox_state):
    """Ensure entertainment groups are parsed correctly."""
    hue = HueResource.from_dict(syncbox_state["hue"])

    assert len(hue.groups) == 2

    tv_area = hue.groups["db7dd240-d061-48bf-84c2-01f086e4bfae"]
    assert tv_area.name == "TV Area"
    assert tv_area.numLights == 5
    assert tv_area.active is False

    pc_area = hue.groups["f7bd7dcb-bbcb-4cd1-b343-126e60575884"]
    assert pc_area.name == "PC Area"
    assert pc_area.numLights == 4


def test_behavior_parsing(syncbox_state):
    """Ensure behavior fields are parsed correctly."""
    behavior = BehaviorResource.from_dict(syncbox_state["behavior"])

    assert behavior.inactivePowersave == 20
    assert behavior.cecPowersave == 1
    assert behavior.usbPowersave == 1
    assert behavior.hpdInputSwitch == 1
    assert behavior.arcBypassMode == 0
    assert behavior.forceDoviNative == 0


def test_behavior_input_parsing(syncbox_state):
    """Ensure per-input behavior settings are parsed correctly."""
    behavior = BehaviorResource.from_dict(syncbox_state["behavior"])

    assert behavior.input1.cecInputSwitch == 1
    assert behavior.input1.linkAutoSync == 0
    assert behavior.input1.hdrMode == 0

    assert behavior.input2.cecInputSwitch == 1


def test_ir_parsing(syncbox_state):
    """Ensure IR resource is parsed correctly."""
    ir = IrResource.from_dict(syncbox_state["ir"])

    assert ir.defaultCodes is True
    assert ir.scan.scanning is False
    assert ir.scan.code is None
    assert ir.codes == {}


def test_registrations_parsing(syncbox_state):
    """Ensure registrations are parsed correctly."""
    registrations = {
        rid: Registration.from_dict(reg)
        for rid, reg in syncbox_state["registrations"].items()
    }

    assert len(registrations) == 2

    assert registrations["1"].appName == "Hue Sync iOS"
    assert registrations["1"].instanceName == "iPhone X"
    assert registrations["1"].role == "user"

    assert registrations["0"].appName == "Hue Sync Android"
    assert registrations["0"].role == "admin"


def test_presets_parsing(syncbox_state):
    """Ensure an empty presets dict is handled correctly."""
    presets = syncbox_state["presets"]
    assert presets == {}

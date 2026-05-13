"""Test the HueSyncBox client."""
from unittest.mock import AsyncMock, patch

import pytest

from aiohue.syncbox import HueSyncBox
from aiohue.syncbox.errors import (
    SyncBoxApiLevelError,
    SyncBoxAuthenticationError,
    SyncBoxInvalidStateError,
    SyncBoxRequestError,
)


@pytest.fixture
def box():
    """Return a HueSyncBox instance with a fake token."""
    return HueSyncBox("192.168.1.12", "fake-token")


async def test_get_state_populates_resources(box, syncbox_state):
    """Ensure get_state parses all resources from the root endpoint."""
    with patch.object(box, "_request", AsyncMock(return_value=syncbox_state)):
        await box.get_state()

    assert box._device.name == "My Sync Box"
    assert box._device.apiLevel == 7
    assert box._execution.mode == "powersave"
    assert box._execution.brightness == 122
    assert box._hdmi.input2.name == "Gaming"
    assert box._hue.connectionState == "connected"
    assert len(box._hue.groups) == 2
    assert len(box._registrations) == 2
    assert box._presets == {}


async def test_get_state_raises_on_low_api_level(box, syncbox_state):
    """Ensure get_state raises SyncBoxApiLevelError for apiLevel < 7."""
    low_level_state = {
        **syncbox_state,
        "device": {**syncbox_state["device"], "apiLevel": 6},
    }
    with patch.object(box, "_request", AsyncMock(return_value=low_level_state)):
        with pytest.raises(SyncBoxApiLevelError) as exc_info:
            await box.get_state()

    assert exc_info.value.api_level == 6


async def test_get_device_info(box, syncbox_state):
    """Ensure get_device_info parses the device resource."""
    with patch.object(
        box, "_request", AsyncMock(return_value=syncbox_state["device"])
    ):
        device = await box.get_device_info()

    assert device.uniqueId == "C42996000000"
    assert device.firmwareVersion == "1.7.4"


async def test_get_device_info_raises_on_low_api_level(box, syncbox_state):
    """Ensure get_device_info raises SyncBoxApiLevelError for apiLevel < 7."""
    low_level_device = {**syncbox_state["device"], "apiLevel": 4}
    with patch.object(box, "_request", AsyncMock(return_value=low_level_device)):
        with pytest.raises(SyncBoxApiLevelError):
            await box.get_device_info()


async def test_execution_get(box, syncbox_state):
    """Ensure execution.get() parses and caches the execution resource."""
    with patch.object(
        box, "_request", AsyncMock(return_value=syncbox_state["execution"])
    ):
        execution = await box.execution.get()

    assert execution.mode == "powersave"
    assert execution.syncActive is False
    assert box._execution is execution


async def test_execution_set_mode(box):
    """Ensure set_mode issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.execution.set_mode("video")

    mock_request.assert_called_once_with("PUT", "/execution", json={"mode": "video"})


async def test_execution_set_sync_active(box):
    """Ensure set_sync_active issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.execution.set_sync_active(True)

    mock_request.assert_called_once_with(
        "PUT", "/execution", json={"syncActive": True}
    )


async def test_execution_toggle_sync(box):
    """Ensure toggle_sync issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.execution.toggle_sync()

    mock_request.assert_called_once_with(
        "PUT", "/execution", json={"toggleSyncActive": True}
    )


async def test_execution_set_brightness(box):
    """Ensure set_brightness issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.execution.set_brightness(150)

    mock_request.assert_called_once_with(
        "PUT", "/execution", json={"brightness": 150}
    )


async def test_execution_set_hdmi_source(box):
    """Ensure set_hdmi_source issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.execution.set_hdmi_source("input3")

    mock_request.assert_called_once_with(
        "PUT", "/execution", json={"hdmiSource": "input3"}
    )


async def test_execution_set_video_settings(box):
    """Ensure set_video_settings issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.execution.set_video_settings(
            intensity="high", background_lighting=False
        )

    mock_request.assert_called_once_with(
        "PUT",
        "/execution",
        json={"video": {"intensity": "high", "backgroundLighting": False}},
    )


async def test_execution_set_music_settings(box):
    """Ensure set_music_settings issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.execution.set_music_settings(
            intensity="subtle", palette="happyCalm"
        )

    mock_request.assert_called_once_with(
        "PUT",
        "/execution",
        json={"music": {"intensity": "subtle", "palette": "happyCalm"}},
    )


async def test_execution_increment_brightness(box):
    """Ensure increment_brightness issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.execution.increment_brightness(-20)

    mock_request.assert_called_once_with(
        "PUT", "/execution", json={"incrementBrightness": -20}
    )


async def test_execution_cycle_hdmi_source(box):
    """Ensure cycle_hdmi_source issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.execution.cycle_hdmi_source("previous")

    mock_request.assert_called_once_with(
        "PUT", "/execution", json={"cycleHdmiSource": "previous"}
    )


async def test_execution_activate_preset(box):
    """Ensure activate_preset issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.execution.activate_preset("abc12345")

    mock_request.assert_called_once_with(
        "PUT", "/execution", json={"preset": "abc12345"}
    )


async def test_hdmi_get(box, syncbox_state):
    """Ensure hdmi.get() parses and caches the hdmi resource."""
    with patch.object(
        box, "_request", AsyncMock(return_value=syncbox_state["hdmi"])
    ):
        hdmi = await box.hdmi.get()

    assert hdmi.input1.name == "HDMI 1"
    assert hdmi.input4.type == "shield"
    assert box._hdmi is hdmi


async def test_hdmi_set_input_name(box):
    """Ensure set_input_name issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.hdmi.set_input_name("input2", "PlayStation")

    mock_request.assert_called_once_with(
        "PUT", "/hdmi/input2", json={"name": "PlayStation"}
    )


async def test_behavior_get(box, syncbox_state):
    """Ensure behavior.get() parses and caches the behavior resource."""
    with patch.object(
        box, "_request", AsyncMock(return_value=syncbox_state["behavior"])
    ):
        behavior = await box.behavior.get()

    assert behavior.inactivePowersave == 20
    assert behavior.cecPowersave == 1
    assert box._behavior is behavior


async def test_behavior_set_inactive_powersave(box):
    """Ensure set_inactive_powersave issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.behavior.set_inactive_powersave(30)

    mock_request.assert_called_once_with(
        "PUT", "/behavior", json={"inactivePowersave": 30}
    )


async def test_behavior_set_input_behavior(box):
    """Ensure set_input_behavior issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.behavior.set_input_behavior("input1", link_auto_sync=1, hdr_mode=2)

    mock_request.assert_called_once_with(
        "PUT", "/behavior/input1", json={"linkAutoSync": 1, "hdrMode": 2}
    )


async def test_ir_get(box, syncbox_state):
    """Ensure ir.get() parses and caches the ir resource."""
    with patch.object(
        box, "_request", AsyncMock(return_value=syncbox_state["ir"])
    ):
        ir = await box.ir.get()

    assert ir.defaultCodes is True
    assert ir.scan.scanning is False
    assert box._ir is ir


async def test_ir_start_scan(box):
    """Ensure start_scan issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.ir.start_scan()

    mock_request.assert_called_once_with(
        "PUT", "/ir/scan", json={"scanning": True}
    )


async def test_ir_add_code(box):
    """Ensure add_code issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.ir.add_code(
            "AABBCCDD",
            name="Toggle sync",
            execution={"toggleSyncActive": True},
        )

    mock_request.assert_called_once_with(
        "PUT",
        "/ir/codes/AABBCCDD",
        json={"name": "Toggle sync", "execution": {"toggleSyncActive": True}},
    )


async def test_registrations_get_all(box, syncbox_state):
    """Ensure registrations.get_all() parses all registrations."""
    with patch.object(
        box, "_request", AsyncMock(return_value=syncbox_state["registrations"])
    ):
        registrations = await box.registrations.get_all()

    assert len(registrations) == 2
    assert registrations["1"].appName == "Hue Sync iOS"
    assert registrations["0"].role == "admin"


async def test_registrations_delete(box):
    """Ensure registrations.delete() issues the correct DELETE request."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.registrations.delete("1")

    mock_request.assert_called_once_with("DELETE", "/registrations/1")


async def test_presets_create(box):
    """Ensure presets.create() issues the correct POST and returns the id."""
    mock_request = AsyncMock(return_value={"presetId": "abc12345"})
    with patch.object(box, "_request", mock_request):
        preset_id = await box.presets.create(
            name="Movie Night",
            execution={"mode": "video", "brightness": 80},
        )

    assert preset_id == "abc12345"
    mock_request.assert_called_once_with(
        "POST",
        "/presets",
        json={
            "name": "Movie Night",
            "execution": {"mode": "video", "brightness": 80},
        },
    )


async def test_presets_delete(box):
    """Ensure presets.delete() issues the correct DELETE request."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.presets.delete("abc12345")

    mock_request.assert_called_once_with("DELETE", "/presets/abc12345")


async def test_hue_set_bridge(box):
    """Ensure hue.set_bridge() issues the correct PUT payload."""
    mock_request = AsyncMock(return_value={})
    with patch.object(box, "_request", mock_request):
        await box.hue.set_bridge(
            bridge_unique_id="001788FFFE000000",
            username="hue-app-key",
            client_key="AABBCCDDAABBCCDDAABBCCDDAABBCCDD",
        )

    mock_request.assert_called_once_with(
        "PUT",
        "/hue",
        json={
            "bridgeUniqueId": "001788FFFE000000",
            "username": "hue-app-key",
            "clientKey": "AABBCCDDAABBCCDDAABBCCDDAABBCCDD",
        },
    )

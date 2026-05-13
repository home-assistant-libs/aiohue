"""
Example: Using the Hue Sync Box client.

Run with:
    python examples/syncbox_example.py
"""
from __future__ import annotations

import asyncio
import sys

# Add repo root to path when running directly
sys.path.insert(0, ".")

from aiohue.syncbox import HueSyncBox, SyncBoxApiLevelError, SyncBoxAuthenticationError


SYNCBOX_IP = "192.168.1.x"     # Replace with your Sync Box IP
ACCESS_TOKEN = ""                # Leave empty to run the registration flow


async def registration_flow(ip: str) -> str:
    """Walk through the pushlink registration to obtain an access token."""
    print("Starting registration flow.")
    print("Hold the Sync Box button until the LED blinks green, then release.")
    input("Press ENTER here once you have released the button...")

    async with HueSyncBox(ip, ssl=False) as box:
        token, reg_id = await box.register(
            app_name="aiohue",
            instance_name="example",
            poll_interval=1.0,
            timeout=30.0,
        )

    print(f"Registered! registration_id={reg_id}")
    print(f"Access token: {token}")
    print("Save this token for future use.\n")
    return token


async def main() -> None:
    token = ACCESS_TOKEN

    if not token:
        token = await registration_flow(SYNCBOX_IP)

    # ssl=False disables certificate validation – fine for local dev, but in
    # production pass a custom ssl context that validates against hsb_cacert.pem
    async with HueSyncBox(SYNCBOX_IP, token, ssl=False) as box:
        # --- Fetch device info (no auth required) ---
        try:
            device = await box.get_device_info()
            print(f"Device: {device.name} ({device.deviceType})")
            print(f"  Firmware: {device.firmwareVersion}  apiLevel: {device.apiLevel}")
            print(f"  WiFi: {device.wifi.ssid} strength={device.wifi.strength}")
        except SyncBoxApiLevelError as exc:
            print(f"ERROR: {exc}")
            return

        # --- Fetch full state ---
        await box.get_state()
        state_exec = box._execution
        print(f"\nExecution state:")
        print(f"  mode={state_exec.mode}  syncActive={state_exec.syncActive}")
        print(f"  hdmiSource={state_exec.hdmiSource}  brightness={state_exec.brightness}")

        hdmi = box._hdmi
        print(f"\nHDMI inputs:")
        for inp in ("input1", "input2", "input3", "input4"):
            port = getattr(hdmi, inp)
            print(f"  {inp}: {port.name!r} ({port.type}) – {port.status}")

        hue = box._hue
        print(f"\nHue bridge: {hue.bridgeIpAddress}  state={hue.connectionState}")
        for gid, group in hue.groups.items():
            print(f"  group {gid[:8]}…: {group.name!r} ({group.numLights} lights)")

        # --- Control examples ---
        print("\nStarting video sync…")
        await box.execution.set_mode("video")
        await box.execution.set_sync_active(True)
        await box.execution.set_brightness(120)
        await box.execution.set_video_settings(intensity="high", background_lighting=True)

        await asyncio.sleep(3)

        print("Switching to music mode…")
        await box.execution.set_mode("music")
        await box.execution.set_music_settings(intensity="moderate", palette="happyEnergetic")

        await asyncio.sleep(3)

        print("Toggling sync off…")
        await box.execution.toggle_sync()

        # --- Presets ---
        print("\nCreating a preset…")
        preset_id = await box.presets.create(
            name="Movie Night",
            execution={"mode": "video", "brightness": 80, "video": {"intensity": "subtle"}},
        )
        print(f"Created preset: {preset_id}")
        await box.presets.delete(preset_id)
        print("Preset deleted.")


if __name__ == "__main__":
    asyncio.run(main())

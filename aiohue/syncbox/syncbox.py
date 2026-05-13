"""Async client for the Philips Hue HDMI Sync Box API."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

import aiohttp

from .errors import (
    SyncBoxApiLevelError,
    SyncBoxAuthenticationError,
    SyncBoxConnectionError,
    SyncBoxError,
    SyncBoxInvalidStateError,
    SyncBoxRequestError,
)
from .models import (
    BehaviorResource,
    DeviceResource,
    ExecutionResource,
    HdmiResource,
    HueResource,
    IrResource,
    Preset,
    Registration,
)

_LOGGER = logging.getLogger(__name__)

MIN_API_LEVEL = 7
API_PATH = "/api/v1"


class HueSyncBox:
    """
    Async client for the Hue HDMI Sync Box local HTTP API.

    All requests are made over HTTPS (port 443).  In production use you should
    pass a ``websession`` that validates the device certificate against the
    Sync Box CA (hsb_cacert.pem) and confirms that the certificate common name
    matches the device unique id.  Passing ``ssl=False`` is convenient for
    development but must not be used when the Authorization header is present.

    Usage::

        async with HueSyncBox("192.168.1.x", "myAccessToken") as box:
            state = await box.get_state()
            await box.execution.set_mode("video")

    Registration (first-time setup)::

        async with HueSyncBox("192.168.1.x") as box:
            # Instruct the user to hold the button until the LED blinks green
            token, reg_id = await box.register("MyApp", "MyInstance")
            # Save token for future use
    """

    def __init__(
        self,
        host: str,
        access_token: Optional[str] = None,
        *,
        websession: Optional[aiohttp.ClientSession] = None,
        ssl: bool = True,
    ) -> None:
        self._host = host
        self._access_token = access_token
        self._ssl = ssl
        self._websession = websession
        self._owns_session = websession is None

        # Sub-resource controllers (populated after connect / get_state)
        self._device: Optional[DeviceResource] = None
        self._execution: Optional[ExecutionResource] = None
        self._hdmi: Optional[HdmiResource] = None
        self._hue: Optional[HueResource] = None
        self._behavior: Optional[BehaviorResource] = None
        self._ir: Optional[IrResource] = None
        self._registrations: dict[str, Registration] = {}
        self._presets: dict[str, Preset] = {}

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "HueSyncBox":
        if self._owns_session:
            self._websession = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._owns_session and self._websession:
            await self._websession.close()
            self._websession = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def device(self) -> Optional[DeviceResource]:
        """Last fetched device resource."""
        return self._device

    @property
    def execution(self) -> "ExecutionController":
        """Execution resource controller."""
        return ExecutionController(self)

    @property
    def hdmi(self) -> "HdmiController":
        """HDMI resource controller."""
        return HdmiController(self)

    @property
    def hue(self) -> "HueController":
        """Hue bridge connection controller."""
        return HueController(self)

    @property
    def behavior(self) -> "BehaviorController":
        """Behavior resource controller."""
        return BehaviorController(self)

    @property
    def ir(self) -> "IrController":
        """IR resource controller."""
        return IrController(self)

    @property
    def registrations(self) -> "RegistrationController":
        """Registration resource controller."""
        return RegistrationController(self)

    @property
    def presets(self) -> "PresetController":
        """Preset resource controller."""
        return PresetController(self)

    # ------------------------------------------------------------------
    # Low-level HTTP helpers
    # ------------------------------------------------------------------

    def _base_url(self) -> str:
        return f"https://{self._host}{API_PATH}"

    def _headers(self, *, authenticated: bool = True) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if authenticated and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[dict] = None,
        authenticated: bool = True,
    ) -> Any:
        if self._websession is None:
            raise SyncBoxError("Client session not open. Use 'async with HueSyncBox(...)' or call __aenter__.")

        url = f"{self._base_url()}{path}"
        try:
            async with self._websession.request(
                method,
                url,
                headers=self._headers(authenticated=authenticated),
                json=json,
                ssl=self._ssl,
            ) as resp:
                if resp.status == 401:
                    raise SyncBoxAuthenticationError(
                        "Authentication failed. Check your access token."
                    )
                if resp.status == 404:
                    raise SyncBoxRequestError(404, f"Path not found: {path}")
                if resp.status == 500:
                    raise SyncBoxError("Internal device error (HTTP 500).")

                if resp.status == 200:
                    try:
                        return await resp.json(content_type=None)
                    except Exception:
                        return {}

                # 400 with error body
                try:
                    body = await resp.json(content_type=None)
                    code = body.get("error") or body.get("code") or resp.status
                    message = body.get("message", "Bad request")
                    if code == 16:
                        raise SyncBoxInvalidStateError(message)
                    raise SyncBoxRequestError(code, message)
                except (SyncBoxRequestError, SyncBoxInvalidStateError):
                    raise
                except Exception:
                    raise SyncBoxRequestError(resp.status, "Bad request")

        except aiohttp.ClientError as exc:
            raise SyncBoxConnectionError(str(exc)) from exc

    # ------------------------------------------------------------------
    # High-level API
    # ------------------------------------------------------------------

    async def get_device_info(self) -> DeviceResource:
        """Fetch /device without authentication (useful for discovery)."""
        data = await self._request("GET", "/device", authenticated=False)
        device = DeviceResource.from_dict(data)
        self._device = device
        if device.apiLevel < MIN_API_LEVEL:
            raise SyncBoxApiLevelError(device.apiLevel)
        return device

    async def get_state(self) -> dict:
        """
        Fetch the full Sync Box state from the root /api/v1 endpoint.

        Returns the raw dict and also populates all resource properties.
        """
        data = await self._request("GET", "")
        self._device = DeviceResource.from_dict(data.get("device", {}))
        if self._device.apiLevel < MIN_API_LEVEL:
            raise SyncBoxApiLevelError(self._device.apiLevel)
        self._execution = ExecutionResource.from_dict(data.get("execution", {}))
        self._hdmi = HdmiResource.from_dict(data.get("hdmi", {}))
        self._hue = HueResource.from_dict(data.get("hue", {}))
        self._behavior = BehaviorResource.from_dict(data.get("behavior", {}))
        self._ir = IrResource.from_dict(data.get("ir", {}))
        self._registrations = {
            rid: Registration.from_dict(reg)
            for rid, reg in data.get("registrations", {}).items()
        }
        self._presets = {
            pid: Preset.from_dict(preset)
            for pid, preset in data.get("presets", {}).items()
        }
        return data

    async def register(
        self,
        app_name: str,
        instance_name: str,
        *,
        poll_interval: float = 1.0,
        timeout: float = 30.0,
    ) -> tuple[str, str]:
        """
        Register this client with the Sync Box using the pushlink flow.

        The user must press and hold the device button until the LED blinks
        green **before** calling this method (or within the timeout window).

        Returns ``(access_token, registration_id)`` on success.

        Raises ``SyncBoxConnectionError`` if timeout is exceeded without
        the user pressing the button.
        """
        payload = {"appName": app_name, "instanceName": instance_name}
        deadline = asyncio.get_event_loop().time() + timeout
        last_exc: Optional[Exception] = None

        while asyncio.get_event_loop().time() < deadline:
            try:
                data = await self._request(
                    "POST", "/registrations", json=payload, authenticated=False
                )
                token: str = data["accessToken"]
                reg_id: str = data["registrationId"]
                self._access_token = token
                return token, reg_id
            except SyncBoxInvalidStateError as exc:
                # code 16 = button not yet pressed
                last_exc = exc
                await asyncio.sleep(poll_interval)
            except SyncBoxRequestError as exc:
                if exc.code == 16:
                    last_exc = exc
                    await asyncio.sleep(poll_interval)
                else:
                    raise

        raise SyncBoxConnectionError(
            f"Registration timed out after {timeout}s. "
            "Make sure the button was pressed until the LED blinked green."
        ) from last_exc


# ---------------------------------------------------------------------------
# Resource controllers
# ---------------------------------------------------------------------------

class ExecutionController:
    """Controller for /api/v1/execution."""

    def __init__(self, client: HueSyncBox) -> None:
        self._client = client

    async def get(self) -> ExecutionResource:
        """Fetch current execution state."""
        data = await self._client._request("GET", "/execution")
        result = ExecutionResource.from_dict(data)
        self._client._execution = result
        return result

    async def update(self, **kwargs: Any) -> None:
        """
        Update one or more execution attributes atomically.

        Examples::

            await box.execution.update(mode="video")
            await box.execution.update(syncActive=True, brightness=150)
            await box.execution.update(video={"intensity": "high"})
        """
        await self._client._request("PUT", "/execution", json=kwargs)

    async def set_mode(self, mode: str) -> None:
        """Set sync mode: powersave | passthrough | video | game | music | ambient."""
        await self.update(mode=mode)

    async def set_sync_active(self, active: bool) -> None:
        """Enable or disable light syncing."""
        await self.update(syncActive=active)

    async def toggle_sync(self) -> None:
        """Toggle the syncActive state."""
        await self.update(toggleSyncActive=True)

    async def set_hdmi_active(self, active: bool) -> None:
        """Enable (passthrough) or disable (powersave) HDMI output."""
        await self.update(hdmiActive=active)

    async def toggle_hdmi(self) -> None:
        """Toggle HDMI active state."""
        await self.update(toggleHdmiActive=True)

    async def set_hdmi_source(self, source: str) -> None:
        """Switch to an HDMI input: input1 | input2 | input3 | input4."""
        await self.update(hdmiSource=source)

    async def cycle_hdmi_source(self, direction: str = "next") -> None:
        """Cycle HDMI input: next | previous."""
        await self.update(cycleHdmiSource=direction)

    async def set_brightness(self, brightness: int) -> None:
        """Set brightness (0–200, 100 = neutral)."""
        await self.update(brightness=brightness)

    async def increment_brightness(self, delta: int) -> None:
        """Increment or decrement brightness by delta (-200–200)."""
        await self.update(incrementBrightness=delta)

    async def set_intensity(self, intensity: str) -> None:
        """Set intensity for the current sync mode: subtle | moderate | high | intense."""
        await self.update(intensity=intensity)

    async def cycle_intensity(self, direction: str = "next") -> None:
        """Cycle intensity: next | previous."""
        await self.update(cycleIntensity=direction)

    async def cycle_sync_mode(self, direction: str = "next") -> None:
        """Cycle sync mode: next | previous."""
        await self.update(cycleSyncMode=direction)

    async def activate_preset(self, preset_id: str) -> None:
        """Activate a stored preset by id."""
        await self.update(preset=preset_id)

    async def set_video_settings(
        self,
        intensity: Optional[str] = None,
        background_lighting: Optional[bool] = None,
    ) -> None:
        """Update video mode settings."""
        payload: dict = {}
        if intensity is not None:
            payload["intensity"] = intensity
        if background_lighting is not None:
            payload["backgroundLighting"] = background_lighting
        await self.update(video=payload)

    async def set_game_settings(
        self,
        intensity: Optional[str] = None,
        background_lighting: Optional[bool] = None,
    ) -> None:
        """Update game mode settings."""
        payload: dict = {}
        if intensity is not None:
            payload["intensity"] = intensity
        if background_lighting is not None:
            payload["backgroundLighting"] = background_lighting
        await self.update(game=payload)

    async def set_music_settings(
        self,
        intensity: Optional[str] = None,
        palette: Optional[str] = None,
    ) -> None:
        """Update music mode settings."""
        payload: dict = {}
        if intensity is not None:
            payload["intensity"] = intensity
        if palette is not None:
            payload["palette"] = palette
        await self.update(music=payload)


class HdmiController:
    """Controller for /api/v1/hdmi."""

    def __init__(self, client: HueSyncBox) -> None:
        self._client = client

    async def get(self) -> HdmiResource:
        """Fetch current HDMI state."""
        data = await self._client._request("GET", "/hdmi")
        result = HdmiResource.from_dict(data)
        self._client._hdmi = result
        return result

    async def set_input_name(self, input_id: str, name: str) -> None:
        """Rename an HDMI port (input1–input4 or output)."""
        await self._client._request("PUT", f"/hdmi/{input_id}", json={"name": name})

    async def set_input_type(self, input_id: str, device_type: str) -> None:
        """Set the device type icon for an input port."""
        await self._client._request("PUT", f"/hdmi/{input_id}", json={"type": device_type})


class HueController:
    """Controller for /api/v1/hue."""

    def __init__(self, client: HueSyncBox) -> None:
        self._client = client

    async def get(self) -> HueResource:
        """Fetch current Hue bridge connection state."""
        data = await self._client._request("GET", "/hue")
        result = HueResource.from_dict(data)
        self._client._hue = result
        return result

    async def set_bridge(
        self,
        bridge_unique_id: str,
        username: str,
        client_key: str,
    ) -> None:
        """
        Pair the Sync Box with a Hue bridge.

        ``username`` is the Hue application key; ``client_key`` is the 32-char
        hex key needed for Entertainment streaming.
        """
        await self._client._request(
            "PUT",
            "/hue",
            json={
                "bridgeUniqueId": bridge_unique_id,
                "username": username,
                "clientKey": client_key,
            },
        )

    async def set_entertainment_group(self, group_id: str) -> None:
        """Select which entertainment area to sync with."""
        await self._client._request(
            "PUT", "/execution", json={"hueTarget": group_id}
        )


class BehaviorController:
    """Controller for /api/v1/behavior."""

    def __init__(self, client: HueSyncBox) -> None:
        self._client = client

    async def get(self) -> BehaviorResource:
        """Fetch current behavior settings."""
        data = await self._client._request("GET", "/behavior")
        result = BehaviorResource.from_dict(data)
        self._client._behavior = result
        return result

    async def update(self, **kwargs: Any) -> None:
        """Update one or more behavior attributes."""
        await self._client._request("PUT", "/behavior", json=kwargs)

    async def set_inactive_powersave(self, minutes: int) -> None:
        """Set idle-to-powersave timeout in minutes (0 = disabled, max 10000)."""
        await self.update(inactivePowersave=minutes)

    async def set_cec_powersave(self, enabled: bool) -> None:
        """Enable/disable powersave on CEC TV-off signal."""
        await self.update(cecPowersave=int(enabled))

    async def set_input_behavior(
        self,
        input_id: str,
        *,
        cec_input_switch: Optional[int] = None,
        link_auto_sync: Optional[int] = None,
        hdr_mode: Optional[int] = None,
    ) -> None:
        """Update per-input behavior (4K only)."""
        payload: dict = {}
        if cec_input_switch is not None:
            payload["cecInputSwitch"] = cec_input_switch
        if link_auto_sync is not None:
            payload["linkAutoSync"] = link_auto_sync
        if hdr_mode is not None:
            payload["hdrMode"] = hdr_mode
        await self._client._request("PUT", f"/behavior/{input_id}", json=payload)


class IrController:
    """Controller for /api/v1/ir."""

    def __init__(self, client: HueSyncBox) -> None:
        self._client = client

    async def get(self) -> IrResource:
        """Fetch current IR state."""
        data = await self._client._request("GET", "/ir")
        result = IrResource.from_dict(data)
        self._client._ir = result
        return result

    async def start_scan(self) -> None:
        """Enter IR scan mode to capture the next IR code received."""
        await self._client._request("PUT", "/ir/scan", json={"scanning": True})

    async def get_scan_result(self) -> Optional[str]:
        """Return the last scanned IR code (or None if not scanned yet)."""
        data = await self._client._request("GET", "/ir/scan")
        return data.get("code")

    async def add_code(self, code: str, name: str, execution: dict) -> None:
        """Map an IR code to an execution action."""
        await self._client._request(
            "PUT",
            f"/ir/codes/{code}",
            json={"name": name, "execution": execution},
        )

    async def delete_code(self, code: str) -> None:
        """Remove an IR code mapping."""
        await self._client._request("DELETE", f"/ir/codes/{code}")


class RegistrationController:
    """Controller for /api/v1/registrations."""

    def __init__(self, client: HueSyncBox) -> None:
        self._client = client

    async def get_all(self) -> dict[str, Registration]:
        """Fetch all registrations."""
        data = await self._client._request("GET", "/registrations")
        result = {
            rid: Registration.from_dict(reg)
            for rid, reg in data.items()
        }
        self._client._registrations = result
        return result

    async def delete(self, registration_id: str) -> None:
        """Delete a registration (can only delete your own)."""
        await self._client._request("DELETE", f"/registrations/{registration_id}")


class PresetController:
    """Controller for /api/v1/presets."""

    def __init__(self, client: HueSyncBox) -> None:
        self._client = client

    async def get_all(self) -> dict[str, Preset]:
        """Fetch all presets."""
        data = await self._client._request("GET", "/presets")
        result = {pid: Preset.from_dict(p) for pid, p in data.items()}
        self._client._presets = result
        return result

    async def create(self, name: str, execution: dict) -> str:
        """Create a new preset. Returns the new preset id."""
        data = await self._client._request(
            "POST", "/presets", json={"name": name, "execution": execution}
        )
        return data.get("presetId", "")

    async def update(self, preset_id: str, *, name: Optional[str] = None, execution: Optional[dict] = None) -> None:
        """Update a preset's name and/or execution settings."""
        payload: dict = {}
        if name is not None:
            payload["name"] = name
        if execution is not None:
            payload["execution"] = execution
        await self._client._request("PUT", f"/presets/{preset_id}", json=payload)

    async def delete(self, preset_id: str) -> None:
        """Delete a preset."""
        await self._client._request("DELETE", f"/presets/{preset_id}")

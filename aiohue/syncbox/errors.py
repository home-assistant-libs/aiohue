"""Exceptions raised by the Hue Sync Box client."""
from __future__ import annotations


class SyncBoxError(Exception):
    """Base exception for all Sync Box errors."""


class SyncBoxAuthenticationError(SyncBoxError):
    """Raised when the access token is missing or invalid (HTTP 401)."""


class SyncBoxInvalidStateError(SyncBoxError):
    """Raised when the request is valid but the device is in a state that cannot fulfil it (error code 16)."""


class SyncBoxRequestError(SyncBoxError):
    """Raised for bad requests (HTTP 400)."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


class SyncBoxConnectionError(SyncBoxError):
    """Raised when a network or connection error occurs."""


class SyncBoxApiLevelError(SyncBoxError):
    """Raised when the device reports apiLevel < 7, which is unsupported."""

    def __init__(self, api_level: int) -> None:
        super().__init__(
            f"Sync Box apiLevel {api_level} is not supported. "
            "Please update the device firmware to apiLevel >= 7."
        )
        self.api_level = api_level

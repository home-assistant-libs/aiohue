"""Aiohue errors.

https://developers.meethue.com/documentation/error-messages
"""


class AiohueException(Exception):
    """Base exception for aiohue."""


class Unauthorized(AiohueException):
    """Username is not authorized."""


class LinkButtonNotPressed(AiohueException):
    """Raised when trying to create a user but link button not pressed."""


class InvalidEvent(AiohueException):
    """Raised when we receive an event that we can not (yet) handle."""


class InvalidAPIVersion(AiohueException):
    """Raised when we're trying to connect to an unsupported bridge version."""


class BridgeBusy(AiohueException):
    """Raised when multiple requests to the bridge failed."""


class BridgeSoftwareOutdated(AiohueException):
    """Raised when the software version of the bridge is (too) outdated."""


ERRORS = {1: Unauthorized, 101: LinkButtonNotPressed}


def raise_from_error(error: dict) -> AiohueException:
    """Raise Exception based on Hue error."""
    _type = error.get("type")
    cls = ERRORS.get(_type, AiohueException)
    raise cls(error["description"])

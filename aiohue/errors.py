"""Aiohue errors.

https://developers.meethue.com/documentation/error-messages
"""


class AiohueException(Exception):
    """Base error for aiohue."""


class Unauthorized(AiohueException):
    """Username is not authorized."""


class LinkButtonNotPressed(AiohueException):
    """Raised when trying to create a user but link button not pressed."""


ERRORS = {1: Unauthorized, 101: LinkButtonNotPressed}


def raise_error(error):
    type = error["type"]
    cls = ERRORS.get(type, AiohueException)
    raise cls("{}: {}".format(type, error["description"]))

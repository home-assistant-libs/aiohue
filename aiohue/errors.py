"""Aiohue errors.

https://developers.meethue.com/documentation/error-messages
"""


class AiohueException(Exception):
    """Base error for aiohue."""


class RequestError(AiohueException):
    """Unable to fulfill request.

    Raised when host or API cannot be reached.
    """


class ResponseError(AiohueException):
    """Invalid response."""


class Unauthorized(AiohueException):
    """Username is not authorized."""


class LinkButtonNotPressed(AiohueException):
    """Raised when trying to create a user but link button not pressed."""


ERRORS = {
    1: Unauthorized,
    101: LinkButtonNotPressed
}


def raise_error(error):
    type = error['type']
    cls = ERRORS.get(type, AiohueException)
    raise cls("{}: {}".format(type, error['description']))

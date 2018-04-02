import asyncio

from aiohttp import client_exceptions

from .config import Config
from .groups import Groups
from .lights import Lights
from .scenes import Scenes
from .sensors import Sensors
from .errors import raise_error, ResponseError, RequestError


class Bridge:
    """Control a Hue bridge."""

    def __init__(self, host, websession, *, username=None):
        self.host = host
        self.username = username
        self.websession = websession
        self.username = username

        self.config = None
        self.groups = None
        self.lights = None
        self.scenes = None
        self.sensors = None

        # self.capabilities = None
        # self.rules = None
        # self.schedules = None

    async def create_user(self, device_type):
        """Create a user.

        https://developers.meethue.com/documentation/configuration-api#71_create_user
        """
        result = await self.request('post', '', {
            'devicetype': device_type
        }, auth=False)
        self.username = result[0]['success']['username']
        return self.username

    async def initialize(self):
        result = await self.request('get', '')

        self.config = Config(result['config'], self.request)
        self.groups = Groups(result['groups'], self.request)
        self.lights = Lights(result['lights'], self.request)
        self.scenes = Scenes(result['scenes'], self.request)
        self.sensors = Sensors(result['sensors'], self.request)

    async def request(self, method, path, json=None, auth=True):
        """Make a request to the API."""
        url = 'http://{}/api/'.format(self.host)
        if auth:
            url += '{}/'.format(self.username)
        url += path

        try:
            async with self.websession.request(method, url, json=json) as res:
                if res.content_type != 'application/json':
                    raise ResponseError(
                        'Invalid content type: {}'.format(res.content_type))
                data = await res.json()
                _raise_on_error(data)
                return data
        except client_exceptions.ClientError as err:
            raise RequestError(
                'Error requesting data from {}: {}'.format(self.host, err)
            ) from None


def _raise_on_error(data):
    """Check response for error message."""
    if isinstance(data, list):
        data = data[0]

    if isinstance(data, dict) and 'error' in data:
        raise_error(data['error'])

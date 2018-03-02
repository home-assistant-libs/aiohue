import async_timeout

from .config import Config
from .groups import Groups
from .lights import Lights
from .errors import raise_error
from .util import get_websession


class Bridge:
    """Control a Hue bridge."""

    def __init__(self, host, *, username=None, websession=None):
        self.host = host
        self.username = username
        self.websession = websession or get_websession()
        self.username = username

        self.config = None
        self.groups = None
        self.lights = None

        # self.capabilities = None
        # self.rules = None
        # self.scenes = None
        # self.schedules = None
        # self.sensors = None

    async def create_user(self, device_type):
        """Create a user.

        https://developers.meethue.com/documentation/configuration-api#71_create_user
        """
        result = await self._request('post', '', {
            'devicetype': device_type
        }, auth=False)
        self.username = result[0]['success']['username']
        return self.username

    async def initialize(self):
        result = await self._request('get', '')
        self.config = Config(result['config'], self._request)
        self.groups = Groups(result['groups'], self._request)
        self.lights = Lights(result['lights'], self._request)

    async def _request(self, method, path, json=None, auth=True):
        """Make a request to the API."""
        url = 'http://{}/api/'.format(self.host)
        if auth:
            url += '{}/'.format(self.username)
        url += path

        async with async_timeout.timeout(10):
            async with self.websession.request(method, url, json=json) as res:
                data = await res.json()
                _raise_on_error(data)
                return data


def _raise_on_error(data):
    """Check response for error message."""
    if isinstance(data, list):
        data = data[0]

    if isinstance(data, dict) and 'error' in data:
        raise_error(data['error'])

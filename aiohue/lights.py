from .api import APIItems


class Lights(APIItems):
    """Represents Hue Lights.

    https://developers.meethue.com/documentation/lights-api
    """

    def __init__(self, raw, request):
        super().__init__(raw, request, 'lights', Light)


class Light:
    """Represents a Hue light."""
    def __init__(self, id, raw, request):
        self.id = id
        self.raw = raw
        self._request = request

    @property
    def uniqueid(self):
        return self.raw['uniqueid']

    @property
    def manufacturername(self):
        return self.raw['manufacturername']

    @property
    def modelid(self):
        return self.raw['modelid']

    @property
    def productname(self):
        # productname added in Bridge API 1.24 (published 03/05/2018)
        return self.raw.get('productname')

    @property
    def name(self):
        return self.raw['name']

    @property
    def state(self):
        return self.raw['state']

    @property
    def type(self):
        return self.raw['type']

    async def set_state(self, on=None, bri=None, hue=None, sat=None, xy=None,
                        ct=None, alert=None, effect=None, transitiontime=None,
                        bri_inc=None, sat_inc=None, hue_inc=None, ct_inc=None,
                        xy_inc=None):
        """Change state of a light."""
        data = {
            key: value for key, value in {
                'on': on,
                'bri': bri,
                'hue': hue,
                'sat': sat,
                'xy': xy,
                'ct': ct,
                'alert': alert,
                'effect': effect,
                'transitiontime': transitiontime,
                'bri_inc': bri_inc,
                'sat_inc': sat_inc,
                'hue_inc': hue_inc,
                'ct_inc': ct_inc,
                'xy_inc': xy_inc,
            }.items() if value is not None
        }

        await self._request('put', 'lights/{}/state'.format(self.id),
                            json=data)

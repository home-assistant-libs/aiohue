from .api import APIItems

TYPE_DAYLIGHT = 'Daylight'

TYPE_CLIP_GENERICFLAG = 'CLIPGenericFlag'
TYPE_CLIP_GENERICSTATUS = 'CLIPGenericStatus'
TYPE_CLIP_HUMIDITY = 'CLIPHumidity'
TYPE_CLIP_LIGHTLEVEL = 'CLIPLightLevel'
TYPE_CLIP_OPENCLOSE = 'CLIPOpenClose'
TYPE_CLIP_PRESENCE = 'CLIPPresence'
TYPE_CLIP_SWITCH = 'CLIPSwitch'
TYPE_CLIP_TEMPERATURE = 'CLIPTemperature'

TYPE_ZGP_SWITCH = 'ZGPSwitch'

TYPE_ZLL_LIGHTLEVEL = 'ZLLLightLevel'
TYPE_ZLL_PRESENCE = 'ZLLPresence'
TYPE_ZLL_SWITCH = 'ZLLSwitch'
TYPE_ZLL_TEMPERATURE = 'ZLLTemperature'

ZGP_SWITCH_BUTTON_1 = 34
ZGP_SWITCH_BUTTON_2 = 16
ZGP_SWITCH_BUTTON_3 = 17
ZGP_SWITCH_BUTTON_4 = 18

ZLL_SWITCH_BUTTON_1_CLICK = 1002
ZLL_SWITCH_BUTTON_2_CLICK = 2002
ZLL_SWITCH_BUTTON_3_CLICK = 3002
ZLL_SWITCH_BUTTON_4_CLICK = 4002

ZLL_SWITCH_BUTTON_1_HOLD = 1003
ZLL_SWITCH_BUTTON_2_HOLD = 2003
ZLL_SWITCH_BUTTON_3_HOLD = 3003
ZLL_SWITCH_BUTTON_4_HOLD = 4003


class Sensors(APIItems):
    """Represents Hue Sensors.

    https://developers.meethue.com/documentation/sensors-api
    """

    def __init__(self, raw, request):
        super().__init__(raw, request, 'sensors', create_sensor)


class GenericSensor:
    """Represents the base Hue sensor."""
    def __init__(self, id, raw, request):
        self.id = id
        self.raw = raw
        self._request = request

    @property
    def name(self):
        return self.raw['name']

    @property
    def type(self):
        return self.raw['type']

    @property
    def modelid(self):
        return self.raw['modelid']

    @property
    def manufacturername(self):
        return self.raw['manufacturername']

    @property
    def productname(self):
        return self.raw.get('productname')

    @property
    def uniqueid(self):
        return self.raw.get('uniqueid')

    @property
    def swversion(self):
        return self.raw.get('swversion')

    @property
    def state(self):
        return self.raw['state']

    @property
    def config(self):
        return self.raw['config']


class GenericCLIPSensor(GenericSensor):
    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._on = raw['config'].get('on')

    @property
    def on(self):
        return self._on


class GenericZGPSensor(GenericSensor):
    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._battery = raw['config'].get('battery')
        self._lastupdated = raw['state'].get('lastupdated')
        self._on = raw['config'].get('on')

    @property
    def battery(self):
        return self._battery

    @property
    def lastupdated(self):
        return self._lastupdated

    @property
    def on(self):
        return self._on


class GenericZLLSensor(GenericSensor):
    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._battery = raw['config'].get('battery')
        self._lastupdated = raw['state'].get('lastupdated')
        self._on = raw['config'].get('on')
        self._reachable = raw['config'].get('reachable')

    @property
    def battery(self):
        return self._battery

    @property
    def lastupdated(self):
        return self._lastupdated

    @property
    def on(self):
        return self._on

    @property
    def reachable(self):
        return self._reachable


class DaylightSensor(GenericSensor):
    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._daylight = raw['state'].get('daylight')
        self._on = raw['config'].get('on')

    @property
    def daylight(self):
        return self._daylight

    @property
    def on(self):
        return self._on

    async def set_config(self, on=None, long=None, lat=None,
                         sunriseoffset=None, sunsetoffset=None):
        """Change config of a Daylight sensor."""
        data = {
            key: value for key, value in {
                'on': on,
                'long': long,
                'lat': lat,
                'sunriseoffset': sunriseoffset,
                'sunsetoffset': sunsetoffset,
            }.items() if value is not None
        }

        await self._request('put', 'sensors/{}/config'.format(self.id),
                            json=data)


class CLIPPresenceSensor(GenericCLIPSensor):
    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._presence = raw['state'].get('presence')

    @property
    def presence(self):
        return self._presence

    async def set_config(self, on=None):
        """Change config of a CLIP Presence sensor."""
        data = {
            key: value for key, value in {
                'on': on,
            }.items() if value is not None
        }

        await self._request('put', 'sensors/{}/config'.format(self.id),
                            json=data)


class ZLLPresenceSensor(GenericZLLSensor):
    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._presence = raw['state'].get('presence')

    @property
    def presence(self):
        return self._presence

    async def set_config(self, on=None, sensitivity=None, sensitivitymax=None):
        """Change config of a ZLL Presence sensor."""
        data = {
            key: value for key, value in {
                'on': on,
                'sensitivity': sensitivity,
                'sensitivitymax': sensitivitymax,
            }.items() if value is not None
        }

        await self._request('put', 'sensors/{}/config'.format(self.id),
                            json=data)


class CLIPSwitchSensor(GenericCLIPSensor):
    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._buttonevent = raw['state'].get('buttonevent')

    def buttonevent(self):
        return self._buttonevent

    async def set_config(self, on=None):
        """Change config of a CLIP Switch sensor."""
        data = {
            key: value for key, value in {
                'on': on,
            }.items() if value is not None
        }

        await self._request('put', 'sensors/{}/config'.format(self.id),
                            json=data)


class ZGPSwitchSensor(GenericZGPSensor):
    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._buttonevent = raw['state'].get('buttonevent')

    @property
    def buttonevent(self):
        if self._buttonevent == ZGP_SWITCH_BUTTON_1:
            return ZGP_SWITCH_BUTTON_1
        elif self._buttonevent == ZGP_SWITCH_BUTTON_2:
            return ZGP_SWITCH_BUTTON_2
        elif self._buttonevent == ZGP_SWITCH_BUTTON_3:
            return ZGP_SWITCH_BUTTON_3
        elif self._buttonevent == ZGP_SWITCH_BUTTON_4:
            return ZGP_SWITCH_BUTTON_4

    async def set_config(self, on=None):
        """Change config of a ZGP Switch sensor."""
        data = {
            key: value for key, value in {
                'on': on,
            }.items() if value is not None
        }

        await self._request('put', 'sensors/{}/config'.format(self.id),
                            json=data)


class ZLLSwitchSensor(GenericZLLSensor):
    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._buttonevent = raw['state'].get('buttonevent')

    @property
    def buttonevent(self):
        if self._buttonevent == ZLL_SWITCH_BUTTON_1_CLICK:
            return ZLL_SWITCH_BUTTON_1_CLICK
        elif self._buttonevent == ZLL_SWITCH_BUTTON_1_HOLD:
            return ZLL_SWITCH_BUTTON_1_HOLD
        elif self._buttonevent == ZLL_SWITCH_BUTTON_2_CLICK:
            return ZLL_SWITCH_BUTTON_2_CLICK
        elif self._buttonevent == ZLL_SWITCH_BUTTON_2_HOLD:
            return ZLL_SWITCH_BUTTON_2_HOLD
        elif self._buttonevent == ZLL_SWITCH_BUTTON_3_CLICK:
            return ZLL_SWITCH_BUTTON_3_CLICK
        elif self._buttonevent == ZLL_SWITCH_BUTTON_3_HOLD:
            return ZLL_SWITCH_BUTTON_3_HOLD
        elif self._buttonevent == ZLL_SWITCH_BUTTON_4_CLICK:
            return ZLL_SWITCH_BUTTON_4_CLICK
        elif self._buttonevent == ZLL_SWITCH_BUTTON_4_HOLD:
            return ZLL_SWITCH_BUTTON_4_HOLD
        else:
            return None

    async def set_config(self, on=None):
        """Change config of a ZLL Switch sensor."""
        data = {
            key: value for key, value in {
                'on': on,
            }.items() if value is not None
        }

        await self._request('put', 'sensors/{}/config'.format(self.id),
                            json=data)


class CLIPLightLevelSensor(GenericCLIPSensor):

    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._dark = raw['state'].get('dark')
        self._daylight = raw['state'].get('daylight')
        self._lightlevel = raw['state'].get('lightlevel')

    @property
    def dark(self):
        return self._dark

    @property
    def daylight(self):
        return self._daylight

    @property
    def lightlevel(self):
        return self._lightlevel

    async def set_config(self, on=None, tholddark=None, tholdoffset=None):
        """Change config of a CLIP LightLevel sensor."""
        data = {
            key: value for key, value in {
                'on': on,
                'tholddark': tholddark,
                'tholdoffset': tholdoffset,
            }.items() if value is not None
        }

        await self._request('put', 'sensors/{}/config'.format(self.id),
                            json=data)


class ZLLLightLevelSensor(GenericZLLSensor):

    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._dark = raw['state'].get('dark')
        self._daylight = raw['state'].get('daylight')
        self._lightlevel = raw['state'].get('lightlevel')

    @property
    def dark(self):
        return self._dark

    @property
    def daylight(self):
        return self._daylight

    @property
    def lightlevel(self):
        return self._lightlevel

    async def set_config(self, on=None, tholddark=None, tholdoffset=None):
        """Change config of a ZLL LightLevel sensor."""
        data = {
            key: value for key, value in {
                'on': on,
                'tholddark': tholddark,
                'tholdoffset': tholdoffset,
            }.items() if value is not None
        }

        await self._request('put', 'sensors/{}/config'.format(self.id),
                            json=data)


class CLIPTemperatureSensor(GenericCLIPSensor):
    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._temperature = raw['state'].get('temperature')

    @property
    def temperature(self):
        return self._temperature

    async def set_config(self, on=None):
        """Change config of a CLIP Temperature sensor."""
        data = {
            key: value for key, value in {
                'on': on,
            }.items() if value is not None
        }

        await self._request('put', 'sensors/{}/config'.format(self.id),
                            json=data)


class ZLLTemperatureSensor(GenericZLLSensor):
    def __init__(self, id, raw, request):
        super().__init__(id, raw, request)
        self._temperature = raw['state'].get('temperature')

    @property
    def temperature(self):
        return self._temperature

    async def set_config(self, on=None):
        """Change config of a ZLL Temperature sensor."""
        data = {
            key: value for key, value in {
                'on': on,
            }.items() if value is not None
        }

        await self._request('put', 'sensors/{}/config'.format(self.id),
                            json=data)


def create_sensor(id, raw, request):
    type = raw['type']

    if type == TYPE_DAYLIGHT:
        return DaylightSensor(id, raw, request)

    elif type == TYPE_CLIP_GENERICFLAG:
        return GenericSensor(id, raw, request)
    elif type == TYPE_CLIP_GENERICSTATUS:
        return GenericSensor(id, raw, request)
    elif type == TYPE_CLIP_HUMIDITY:
        return GenericSensor(id, raw, request)
    elif type == TYPE_CLIP_LIGHTLEVEL:
        return CLIPLightLevelSensor(id, raw, request)
    elif type == TYPE_CLIP_OPENCLOSE:
        return GenericSensor(id, raw, request)
    elif type == TYPE_CLIP_PRESENCE:
        return CLIPPresenceSensor(id, raw, request)
    elif type == TYPE_CLIP_SWITCH:
        return CLIPSwitchSensor(id, raw, request)
    elif type == TYPE_CLIP_TEMPERATURE:
        return CLIPTemperatureSensor(id, raw, request)

    elif type == TYPE_ZGP_SWITCH:
        return ZGPSwitchSensor(id, raw, request)

    elif type == TYPE_ZLL_LIGHTLEVEL:
        return ZLLLightLevelSensor(id, raw, request)
    elif type == TYPE_ZLL_PRESENCE:
        return ZLLPresenceSensor(id, raw, request)
    elif type == TYPE_ZLL_SWITCH:
        return ZLLSwitchSensor(id, raw, request)
    elif type == TYPE_ZLL_TEMPERATURE:
        return ZLLTemperatureSensor(id, raw, request)

    return GenericSensor(id, raw, request)

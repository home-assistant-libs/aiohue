from .api import APIItems

TYPE_HUE_DAYLIGHT = ['Daylight']
TYPE_HUE_GENERICFLAG = ['CLIPGenericFlag']
TYPE_HUE_GENERICSTATUS = ['CLIPGenericStatus']
TYPE_HUE_HUMIDITY = ['CLIPHumidity']
TYPE_HUE_LIGHTLEVEL = ['ZLLLightlevel', 'CLIPLightlevel']
TYPE_HUE_OPENCLOSE = ['CLIPOpenClose']
TYPE_HUE_PRESENCE = ['ZLLPresence', 'CLIPPresence']
TYPE_HUE_SWITCH = ['ZGPSwitch', 'ZLLSwitch', 'CLIPSwitch']
TYPE_HUE_TEMPERATURE = ['ZLLTemperature', 'CLIPTemperature']

MODEL_HUE_TAP = ['SWT001']
MODEL_HUE_DIMMER = ['RWL020', 'RWL021']
MODEL_HUE_MOTION = ['SML001']


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


class HueDaylightSensor(GenericSensor):
    def __init__(self, id, raw, request):
        self._daylight = raw['state'].get('daylight')
        self._on = raw['config'].get('on')
        super().__init__(id, raw, request)

    @property
    def daylight(self):
        return self._daylight

    @property
    def on(self):
        return self._on

    @property
    def state(self):
        return self.daylight


class HueDimmerSwitch(GenericSensor):
    def __init__(self, id, raw, request):
        self._buttonevent = raw['state'].get('buttonevent')
        self._lastupdated = raw['state'].get('lastupdated')
        self._battery = raw['config'].get('battery')
        self._reachable = raw['config'].get('reachable')
        self._on = raw['config'].get('on')
        super().__init__(id, raw, request)

    @property
    def battery(self):
        return self._battery

    @property
    def buttonevent(self):
        if self._buttonevent == 1002:
            return 'ON_CLICK'
        elif self._buttonevent == 1003:
            return 'ON_HOLD'
        elif self._buttonevent == 2002:
            return 'DIM_UP_CLICK'
        elif self._buttonevent == 2003:
            return 'DIM_UP_HOLD'
        elif self._buttonevent == 3002:
            return 'DIM_DOWN_CLICK'
        elif self._buttonevent == 3003:
            return 'DIM_DOWN_HOLD'
        elif self._buttonevent == 4002:
            return 'OFF_CLICK'
        elif self._buttonevent == 4003:
            return 'OFF_HOLD'
        else:
            return None

    @property
    def lastupdated(self):
        return self._lastupdated

    @property
    def on(self):
        return self._on

    @property
    def reachable(self):
        return self._reachable

    @property
    def state(self):
        return self.buttonevent


class HueGenericSwitch(GenericSensor):
    def __init__(self, id, raw, request):
        self._buttonevent = raw['state'].get('buttonevent')
        super().__init__(id, raw, request)

    def buttonevent(self):
        return self._buttonevent

    def state(self):
        return self.buttonevent


class HueTapSwitch(GenericSensor):
    def __init__(self, id, raw, request):
        self._buttonevent = raw['state'].get('buttonevent')
        self._on = raw['config'].get('on')
        super().__init__(id, raw, request)

    @property
    def buttonevent(self):
        if self._buttonevent == 34:
            return 'BUTTON_1'
        elif self._buttonevent == 16:
            return 'BUTTON_2'
        elif self._buttonevent == 17:
            return 'BUTTON_3'
        elif self._buttonevent == 18:
            return 'BUTTON_4'

    @property
    def on(self):
        return self._on

    @property
    def state(self):
        return self.buttonevent


class HueTemperatureSensor(GenericSensor):
    def __init__(self, id, raw, request):
        self._temperature = raw['state'].get('temperature')
        super().__init__(id, raw, request)
        self._uom = '°C'

    @property
    def temperature(self):
        temp = float(self._temperature) / 100
        return temp

    @property
    def state(self):
        return self.temperature

    @property
    def uom(self):
        return self._uom


def create_sensor(id, raw, request):
    type = raw['type']
    modelid = raw['modelid']

    if type in TYPE_HUE_SWITCH:
        if modelid in MODEL_HUE_TAP:
            return HueTapSwitch(id, raw, request)
        elif modelid in MODEL_HUE_DIMMER:
            return HueDimmerSwitch(id, raw, request)
        else:
            return HueGenericSwitch(id, raw, request)

    elif type in TYPE_HUE_DAYLIGHT:
        return HueDaylightSensor(id, raw, request)

    elif type in TYPE_HUE_TEMPERATURE:
        return HueTemperatureSensor(id, raw, request)

    else:
        return GenericSensor(id, raw, request)

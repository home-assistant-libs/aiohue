"""Hue sensor resources."""
from __future__ import annotations
from .api import APIItems

TYPE_DAYLIGHT = "Daylight"

TYPE_CLIP_GENERICFLAG = "CLIPGenericFlag"
TYPE_CLIP_GENERICSTATUS = "CLIPGenericStatus"
TYPE_CLIP_HUMIDITY = "CLIPHumidity"
TYPE_CLIP_LIGHTLEVEL = "CLIPLightLevel"
TYPE_CLIP_OPENCLOSE = "CLIPOpenClose"
TYPE_CLIP_PRESENCE = "CLIPPresence"
TYPE_CLIP_SWITCH = "CLIPSwitch"
TYPE_CLIP_TEMPERATURE = "CLIPTemperature"

TYPE_GEOFENCE = "Geofence"

TYPE_ZGP_SWITCH = "ZGPSwitch"

TYPE_ZLL_LIGHTLEVEL = "ZLLLightLevel"
TYPE_ZLL_PRESENCE = "ZLLPresence"
TYPE_ZLL_ROTARY = "ZLLRelativeRotary"
TYPE_ZLL_SWITCH = "ZLLSwitch"
TYPE_ZLL_TEMPERATURE = "ZLLTemperature"

ZGP_SWITCH_BUTTON_1 = 34
ZGP_SWITCH_BUTTON_2 = 16
ZGP_SWITCH_BUTTON_3 = 17
ZGP_SWITCH_BUTTON_4 = 18

ZLL_SWITCH_BUTTON_1_INITIAL_PRESS = 1000
ZLL_SWITCH_BUTTON_2_INITIAL_PRESS = 2000
ZLL_SWITCH_BUTTON_3_INITIAL_PRESS = 3000
ZLL_SWITCH_BUTTON_4_INITIAL_PRESS = 4000

ZLL_SWITCH_BUTTON_1_HOLD = 1001
ZLL_SWITCH_BUTTON_2_HOLD = 2001
ZLL_SWITCH_BUTTON_3_HOLD = 3001
ZLL_SWITCH_BUTTON_4_HOLD = 4001

ZLL_SWITCH_BUTTON_1_SHORT_RELEASED = 1002
ZLL_SWITCH_BUTTON_2_SHORT_RELEASED = 2002
ZLL_SWITCH_BUTTON_3_SHORT_RELEASED = 3002
ZLL_SWITCH_BUTTON_4_SHORT_RELEASED = 4002

ZLL_SWITCH_BUTTON_1_LONG_RELEASED = 1003
ZLL_SWITCH_BUTTON_2_LONG_RELEASED = 2003
ZLL_SWITCH_BUTTON_3_LONG_RELEASED = 3003
ZLL_SWITCH_BUTTON_4_LONG_RELEASED = 4003

EVENT_BUTTON = "button"
EVENT_LIGHTLEVEL = "light_level"
EVENT_MOTION = "motion"
EVENT_POWER = "device_power"
EVENT_TEMPERATURE = "temperature"


class Sensors(APIItems):
    """Represents Hue Sensors.

    https://developers.meethue.com/documentation/sensors-api
    """

    def __init__(self, logger, raw, request):
        super().__init__(logger, raw, request, "sensors", create_sensor)


class GenericSensor:
    """Represents the base Hue sensor."""

    ITEM_TYPE = "sensors"

    def __init__(self, id, raw, request):
        self.id = id
        self.raw = raw
        self._request = request
        self.last_event = None

    @property
    def name(self):
        return self.raw["name"]

    @property
    def type(self):
        return self.raw["type"]

    @property
    def modelid(self):
        return self.raw["modelid"]

    @property
    def manufacturername(self):
        return self.raw["manufacturername"]

    @property
    def productname(self):
        return self.raw.get("productname")

    @property
    def uniqueid(self):
        return self.raw.get("uniqueid")

    @property
    def swversion(self):
        return self.raw.get("swversion")

    @property
    def state(self):
        return self.raw["state"]

    @property
    def config(self):
        return self.raw["config"]


class GenericCLIPSensor(GenericSensor):
    @property
    def battery(self):
        return self.raw["state"].get("battery")

    @property
    def lastupdated(self):
        return self.raw["state"]["lastupdated"]

    @property
    def on(self):
        return self.raw["config"]["on"]

    @property
    def reachable(self):
        return self.raw["config"]["reachable"]

    @property
    def url(self):
        return self.raw["config"].get("url")

    async def set_config(self, config):
        """Change config of a CLIP sensor."""
        await self._request("put", "sensors/{}/config".format(self.id), json=config)

    async def set_state(self, state):
        """Change state of a CLIP sensor."""
        await self._request("put", "sensors/{}/state".format(self.id), json=state)


class GenericZLLSensor(GenericSensor):
    @property
    def battery(self):
        return self.raw["state"].get("battery", self.raw["config"].get("battery"))

    @property
    def lastupdated(self):
        return self.raw["state"].get("lastupdated")

    @property
    def on(self):
        return self.raw["config"]["on"]

    @property
    def reachable(self):
        return self.raw["config"]["reachable"]


class GenericSwitchSensor:
    @property
    def buttonevent(self):
        return self.raw["state"]["buttonevent"]

    @property
    def inputs(self):
        return self.raw.get("capabilities", {}).get("inputs")

    async def set_config(self, on=None):
        """Change config of a Switch sensor."""
        data = {} if on is None else {"on": on}

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class DaylightSensor(GenericSensor):
    @property
    def configured(self):
        return self.raw["config"]["configured"]

    @property
    def daylight(self):
        return self.raw["state"]["daylight"]

    @property
    def on(self):
        return self.raw["config"]["on"]

    @property
    def sunriseoffset(self):
        return self.raw["config"]["sunriseoffset"]

    @property
    def sunsetoffset(self):
        return self.raw["config"]["sunsetoffset"]

    async def set_config(
        self, on=None, long=None, lat=None, sunriseoffset=None, sunsetoffset=None
    ):
        """Change config of a Daylight sensor."""
        data = {
            key: value
            for key, value in {
                "on": on,
                "long": long,
                "lat": lat,
                "sunriseoffset": sunriseoffset,
                "sunsetoffset": sunsetoffset,
            }.items()
            if value is not None
        }

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class GeofenceSensor(GenericSensor):
    @property
    def on(self):
        return self.raw["config"]["on"]

    @property
    def presence(self):
        return self.raw["state"]["presence"]

    @property
    def reachable(self):
        return self.raw["config"]["reachable"]

    async def set_config(self, on=None):
        """Change config of the Geofence sensor."""
        data = {} if on is None else {"on": on}

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class CLIPPresenceSensor(GenericCLIPSensor):
    @property
    def presence(self):
        return self.raw["state"]["presence"]

    async def set_config(self, on=None):
        """Change config of a CLIP Presence sensor."""
        data = {} if on is None else {"on": on}

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class ZLLPresenceSensor(GenericZLLSensor):
    @property
    def presence(self):
        return self.raw["state"]["presence"]

    async def set_config(self, on=None, sensitivity=None, sensitivitymax=None):
        """Change config of a ZLL Presence sensor."""
        data = {
            key: value
            for key, value in {
                "on": on,
                "sensitivity": sensitivity,
                "sensitivitymax": sensitivitymax,
            }.items()
            if value is not None
        }

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class ZLLRotarySensor(GenericZLLSensor):
    @property
    def rotaryevent(self):
        return self.raw["state"]["rotaryevent"]

    @property
    def expectedrotation(self):
        return self.raw["state"]["expectedrotation"]

    @property
    def expectedeventduration(self):
        return self.raw["state"]["expectedeventduration"]

    async def set_config(self, on=None):
        """Change config of a ZLL Rotary sensor."""
        data = {} if on is None else {"on": on}

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class CLIPSwitchSensor(GenericCLIPSensor):
    @property
    def buttonevent(self):
        return self.raw["state"]["buttonevent"]

    async def set_config(self, on=None):
        """Change config of a CLIP Switch sensor."""
        data = {} if on is None else {"on": on}

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class ZGPSwitchSensor(GenericSensor, GenericSwitchSensor):
    @property
    def lastupdated(self):
        return self.raw["state"].get("lastupdated")

    @property
    def on(self):
        return self.raw["config"]["on"]


class ZLLSwitchSensor(GenericZLLSensor, GenericSwitchSensor):
    pass


class CLIPLightLevelSensor(GenericCLIPSensor):
    @property
    def dark(self):
        return self.raw["state"]["dark"]

    @property
    def daylight(self):
        return self.raw["state"]["daylight"]

    @property
    def lightlevel(self):
        return self.raw["state"]["lightlevel"]

    @property
    def tholddark(self):
        return self.raw["config"]["tholddark"]

    @property
    def tholdoffset(self):
        return self.raw["config"]["tholdoffset"]

    async def set_config(self, on=None, tholddark=None, tholdoffset=None):
        """Change config of a CLIP LightLevel sensor."""
        data = {
            key: value
            for key, value in {
                "on": on,
                "tholddark": tholddark,
                "tholdoffset": tholdoffset,
            }.items()
            if value is not None
        }

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class ZLLLightLevelSensor(GenericZLLSensor):
    @property
    def dark(self):
        return self.raw["state"]["dark"]

    @property
    def daylight(self):
        return self.raw["state"]["daylight"]

    @property
    def lightlevel(self):
        return self.raw["state"]["lightlevel"]

    @property
    def tholddark(self):
        return self.raw["config"]["tholddark"]

    @property
    def tholdoffset(self):
        return self.raw["config"]["tholdoffset"]

    async def set_config(self, on=None, tholddark=None, tholdoffset=None):
        """Change config of a ZLL LightLevel sensor."""
        data = {
            key: value
            for key, value in {
                "on": on,
                "tholddark": tholddark,
                "tholdoffset": tholdoffset,
            }.items()
            if value is not None
        }

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class CLIPTemperatureSensor(GenericCLIPSensor):
    @property
    def temperature(self):
        return self.raw["state"]["temperature"]

    async def set_config(self, on=None):
        """Change config of a CLIP Temperature sensor."""
        data = {} if on is None else {"on": on}

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class ZLLTemperatureSensor(GenericZLLSensor):
    @property
    def temperature(self):
        return self.raw["state"]["temperature"]

    async def set_config(self, on=None):
        """Change config of a ZLL Temperature sensor."""
        data = {} if on is None else {"on": on}

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class CLIPGenericFlagSensor(GenericCLIPSensor):
    @property
    def flag(self):
        return self.raw["state"]["flag"]

    async def set_config(self, on=None):
        """Change config of a CLIP Generic Flag sensor."""
        data = {} if on is None else {"on": on}

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class CLIPGenericStatusSensor(GenericCLIPSensor):
    @property
    def status(self):
        return self.raw["state"]["status"]

    async def set_config(self, on=None):
        """Change config of a CLIP Generic Status sensor."""
        data = {} if on is None else {"on": on}

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class CLIPHumiditySensor(GenericCLIPSensor):
    @property
    def humidity(self):
        return self.raw["state"]["humidity"]

    async def set_config(self, on=None):
        """Change config of a CLIP Humidity sensor."""
        data = {} if on is None else {"on": on}

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


class CLIPOpenCloseSensor(GenericCLIPSensor):
    @property
    def open(self):
        return self.raw["state"]["open"]

    async def set_config(self, on=None):
        """Change config of a CLIP Open Close sensor."""
        data = {} if on is None else {"on": on}

        await self._request("put", "sensors/{}/config".format(self.id), json=data)


def create_sensor(id, raw, request):
    type = raw["type"]

    if type == TYPE_DAYLIGHT:
        return DaylightSensor(id, raw, request)

    elif type == TYPE_CLIP_GENERICFLAG:
        return CLIPGenericFlagSensor(id, raw, request)
    elif type == TYPE_CLIP_GENERICSTATUS:
        return CLIPGenericStatusSensor(id, raw, request)
    elif type == TYPE_CLIP_HUMIDITY:
        return CLIPHumiditySensor(id, raw, request)
    elif type == TYPE_CLIP_LIGHTLEVEL:
        return CLIPLightLevelSensor(id, raw, request)
    elif type == TYPE_CLIP_OPENCLOSE:
        return CLIPOpenCloseSensor(id, raw, request)
    elif type == TYPE_CLIP_PRESENCE:
        return CLIPPresenceSensor(id, raw, request)
    elif type == TYPE_CLIP_SWITCH:
        return CLIPSwitchSensor(id, raw, request)
    elif type == TYPE_CLIP_TEMPERATURE:
        return CLIPTemperatureSensor(id, raw, request)

    elif type == TYPE_GEOFENCE:
        return GeofenceSensor(id, raw, request)

    elif type == TYPE_ZGP_SWITCH:
        return ZGPSwitchSensor(id, raw, request)

    elif type == TYPE_ZLL_LIGHTLEVEL:
        return ZLLLightLevelSensor(id, raw, request)
    elif type == TYPE_ZLL_PRESENCE:
        return ZLLPresenceSensor(id, raw, request)
    elif type == TYPE_ZLL_ROTARY:
        return ZLLRotarySensor(id, raw, request)
    elif type == TYPE_ZLL_SWITCH:
        return ZLLSwitchSensor(id, raw, request)
    elif type == TYPE_ZLL_TEMPERATURE:
        return ZLLTemperatureSensor(id, raw, request)

    else:
        return GenericSensor(id, raw, request)

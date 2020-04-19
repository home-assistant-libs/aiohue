from .api import APIItems


class Groups(APIItems):
    """Represents Hue Groups.

    https://developers.meethue.com/documentation/groups-api
    """

    def __init__(self, raw, request):
        super().__init__(raw, request, "groups", Group)

    async def get_all_lights_group(self):
        """Special all lights group."""
        return Group("0", await self._request("get", "groups/0"), self._request)


class Group:
    """Represents a Hue Group."""

    def __init__(self, id, raw, request):
        self.id = id
        self.raw = raw
        self._request = request

    @property
    def name(self):
        return self.raw["name"]

    @property
    def uniqueid(self):
        """Unique ID for the group.

        Requires API version 1.9+ and only for groups that are the type
        Luminaire or Lightsource.
        """
        return self.raw.get("uniqueid")

    @property
    def action(self):
        return self.raw["action"]

    @property
    def state(self):
        return self.raw["state"]

    @property
    def type(self):
        return self.raw["type"]

    @property
    def lights(self):
        return self.raw["lights"]

    async def set_action(
        self,
        on=None,
        bri=None,
        hue=None,
        sat=None,
        xy=None,
        ct=None,
        alert=None,
        effect=None,
        transitiontime=None,
        bri_inc=None,
        sat_inc=None,
        hue_inc=None,
        ct_inc=None,
        xy_inc=None,
        scene=None,
    ):
        """Change action of a group."""
        data = {
            key: value
            for key, value in {
                "on": on,
                "bri": bri,
                "hue": hue,
                "sat": sat,
                "xy": xy,
                "ct": ct,
                "alert": alert,
                "effect": effect,
                "transitiontime": transitiontime,
                "bri_inc": bri_inc,
                "sat_inc": sat_inc,
                "hue_inc": hue_inc,
                "ct_inc": ct_inc,
                "xy_inc": xy_inc,
                "scene": scene,
            }.items()
            if value is not None
        }

        await self._request("put", "groups/{}/action".format(self.id), json=data)

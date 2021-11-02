"""Controller holding and managing HUE resources that are of the config type."""
from __future__ import annotations

from typing import TYPE_CHECKING, Type, Union

from aiohue.v2.models.bridge_home import BridgeHome
from aiohue.v2.models.device import Device
from aiohue.v2.models.entertainment import Entertainment, EntertainmentConfiguration

from ..models.bridge import Bridge
from ..models.resource import ResourceTypes
from .base import BaseResourcesController, GroupedControllerBase

if TYPE_CHECKING:
    from .. import HueBridgeV2


class BridgeController(BaseResourcesController[Type[Bridge]]):
    """Controller holding and managing HUE resources of type `bridge`."""

    item_type = ResourceTypes.BRIDGE

    @property
    def id(self) -> str | None:
        """Return id of the only/first bridge found in items."""
        for item in self.items:
            return item.id
        return None


class BridgeHomeController(BaseResourcesController[Type[BridgeHome]]):
    """Controller holding and managing HUE resources of type `bridge_home`."""

    item_type = ResourceTypes.BRIDGE_HOME


class EntertainmentController(BaseResourcesController[Type[Entertainment]]):
    """Controller holding and managing HUE resources of type `entertainment`."""

    item_type = ResourceTypes.ENTERTAINMENT


class EntertainmentConfigurationController(
    BaseResourcesController[Type[EntertainmentConfiguration]]
):
    """Controller holding and managing HUE resources of type `entertainment_configuration`."""

    item_type = ResourceTypes.ENTERTAINMENT_CONFIGURATION


class ConfigController(
    GroupedControllerBase[
        Union[Bridge, BridgeHome, Entertainment, EntertainmentConfiguration]
    ]
):
    """Controller holding and managing HUE resources thare are of the config type."""

    @property
    def bridge_id(self) -> str | None:
        """Return id of bridge we're connected to."""
        if bridge := self.bridge:
            return bridge.bridge_id
        return None

    @property
    def name(self) -> str | None:
        """Return name of bridge we're connected to."""
        if bridge_device := self.bridge_device:
            return bridge_device.metadata.name
        return None

    @property
    def mac_address(self) -> str | None:
        """Return mac address of bridge we're connected to."""
        if bridge_device := self.bridge_device:
            for service in bridge_device.services:
                if service.rtype == ResourceTypes.ZIGBEE_CONNECTIVITY:
                    return self._bridge.sensors.zigbee_connectivity[
                        service.rid
                    ].mac_address
        return None

    @property
    def model_id(self) -> str | None:
        """Return model ID of bridge we're connected to."""
        if bridge_device := self.bridge_device:
            return bridge_device.product_data.model_id
        return None

    @property
    def software_version(self) -> str | None:
        """Return software version of bridge we're connected to."""
        if bridge_device := self.bridge_device:
            return bridge_device.product_data.software_version
        return None

    @property
    def bridge(self) -> Bridge | None:
        """Return the only/first bridge found in items of resource `bridge`."""
        # the Hue resource system in V2 is generic and even the bridge object is returned as array
        # there should be only one object returned here
        for item in self.bridges:
            return item
        return None

    @property
    def bridge_device(self) -> Device | None:
        """Return the device object belonging to the bridge."""
        # the Hue resource system in V2 is generic and even the bridge metadata
        # can (only) be retrieved as a device object
        # do the plumbing by looking it up here.
        # this device object contains the metadata that is more or like comparable
        # with the V1 output like it's name and software version.
        if bridge := self.bridge:
            for device in self._bridge.devices:
                for service in device.services:
                    if service.rid == bridge.id:
                        return device
        return None

    def __init__(self, bridge: "HueBridgeV2") -> None:
        """Initialize underlying controller instances."""
        self.bridges = BridgeController(bridge)
        self.bridge_home = BridgeHomeController(bridge)
        self.entertainment = EntertainmentController(bridge)
        self.entertainment_configuration = EntertainmentConfigurationController(bridge)
        super().__init__(
            bridge,
            [
                self.bridges,
                self.bridge_home,
                self.entertainment,
                self.entertainment_configuration,
            ],
        )

"""Controller holding and managing HUE resources that are of the config type."""

from typing import TYPE_CHECKING, Union

from awesomeversion import AwesomeVersion

from aiohue.errors import BridgeSoftwareOutdated
from aiohue.util import mac_from_bridge_id
from aiohue.v2.models.behavior_instance import BehaviorInstance, BehaviorInstancePut
from aiohue.v2.models.behavior_script import BehaviorScript
from aiohue.v2.models.bridge import Bridge
from aiohue.v2.models.bridge_home import BridgeHome
from aiohue.v2.models.device import Device
from aiohue.v2.models.entertainment import Entertainment
from aiohue.v2.models.entertainment_configuration import EntertainmentConfiguration
from aiohue.v2.models.homekit import Homekit
from aiohue.v2.models.matter import Matter
from aiohue.v2.models.matter_fabric import MatterFabric
from aiohue.v2.models.resource import ResourceTypes

from .base import BaseResourcesController, GroupedControllerBase

if TYPE_CHECKING:
    from aiohue.v2 import HueBridgeV2


class BridgeController(BaseResourcesController[type[Bridge]]):
    """Controller holding and managing HUE resources of type `bridge`."""

    item_type = ResourceTypes.BRIDGE
    item_cls = Bridge

    @property
    def id(self) -> str | None:
        """Return id of the only/first bridge found in items."""
        for item in self.items:
            return item.id
        return None


class BridgeHomeController(BaseResourcesController[type[BridgeHome]]):
    """Controller holding and managing HUE resources of type `bridge_home`."""

    item_type = ResourceTypes.BRIDGE_HOME
    item_cls = BridgeHome


class EntertainmentController(BaseResourcesController[type[Entertainment]]):
    """Controller holding and managing HUE resources of type `entertainment`."""

    item_type = ResourceTypes.ENTERTAINMENT
    item_cls = Entertainment
    allow_parser_error = True


class EntertainmentConfigurationController(
    BaseResourcesController[type[EntertainmentConfiguration]]
):
    """Controller holding and managing HUE resources of type `entertainment_configuration`."""

    item_type = ResourceTypes.ENTERTAINMENT_CONFIGURATION
    item_cls = EntertainmentConfiguration
    allow_parser_error = True


class HomekitController(BaseResourcesController[type[Homekit]]):
    """Controller holding and managing HUE resources of type `homekit`."""

    item_type = ResourceTypes.HOMEKIT
    item_cls = Homekit
    allow_parser_error = True


class MatterController(BaseResourcesController[type[Matter]]):
    """Controller holding and managing HUE resources of type `matter`."""

    item_type = ResourceTypes.MATTER
    item_cls = Matter
    allow_parser_error = True


class MatterFabricController(BaseResourcesController[type[MatterFabric]]):
    """Controller holding and managing HUE resources of type `matter_fabric`."""

    item_type = ResourceTypes.MATTER_FABRIC
    item_cls = MatterFabric
    allow_parser_error = True


class BehaviorScriptController(BaseResourcesController[type[BehaviorScript]]):
    """Controller holding and managing HUE resources of type `behavior_script`."""

    item_type = ResourceTypes.BEHAVIOR_SCRIPT
    item_cls = BehaviorScript
    allow_parser_error = True


class BehaviorInstanceController(BaseResourcesController[type[BehaviorInstance]]):
    """Controller holding and managing HUE resources of type `behavior_instance`."""

    item_type = ResourceTypes.BEHAVIOR_INSTANCE
    item_cls = BehaviorInstance
    allow_parser_error = True

    async def set_enabled(self, id: str, enabled: bool) -> None:
        """Enable/Disable sensor."""
        await self.update(id, BehaviorInstancePut(enabled=enabled))


class ConfigController(
    GroupedControllerBase[
        Union[Bridge, BridgeHome, Entertainment, EntertainmentConfiguration]  # noqa: UP007
    ]
):
    """
    Controller holding and managing HUE resources there are of the config type.

    Note that the properties will raise AttributeError if not connected to a bridge.
    """

    @property
    def bridge_id(self) -> str:
        """Return bridge_id of bridge we're connected to."""
        return self.bridge.bridge_id

    @property
    def name(self) -> str:
        """Return name of bridge we're connected to."""
        return self.bridge_device.metadata.name

    @property
    def mac_address(self) -> str:
        """Return mac address of bridge we're connected to."""
        # the network mac is not available in api so we parse it from the id
        return mac_from_bridge_id(self.bridge_id)

    @property
    def model_id(self) -> str:
        """Return model ID of bridge we're connected to."""
        return self.bridge_device.product_data.model_id

    @property
    def software_version(self) -> str:
        """Return software version of bridge we're connected to."""
        return self.bridge_device.product_data.software_version

    @property
    def bridge(self) -> Bridge:
        """Return the only/first bridge found in items of resource `bridge`."""
        # the Hue resource system in V2 is generic and even the bridge object is returned as array
        # there should be only one object returned here
        return next(item for item in self.bridges)

    @property
    def bridge_device(self) -> Device:
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
        raise AttributeError("bridge_device")

    def check_version(self, version: str) -> bool:
        """Check if bridge version is equal to (or higher than) given version."""
        current = AwesomeVersion(self.software_version)
        required = AwesomeVersion(version)
        return current >= required

    def require_version(self, version: str) -> None:
        """Raise exception if Bridge version is lower than given minimal version."""
        if not self.check_version(version):
            raise BridgeSoftwareOutdated(
                f"Bridge software version outdated. Minimal required version is {version}"
            )

    def __init__(self, bridge: "HueBridgeV2") -> None:
        """Initialize underlying controller instances."""
        self.bridges = BridgeController(bridge)
        self.bridge_home = BridgeHomeController(bridge)
        self.entertainment = EntertainmentController(bridge)
        self.entertainment_configuration = EntertainmentConfigurationController(bridge)
        self.homekit = HomekitController(bridge)
        self.matter = MatterController(bridge)
        self.matter_fabric = MatterFabricController(bridge)
        self.behavior_script = BehaviorScriptController(bridge)
        self.behavior_instance = BehaviorInstanceController(bridge)
        super().__init__(
            bridge,
            [
                self.bridges,
                self.bridge_home,
                self.entertainment,
                self.entertainment_configuration,
                self.homekit,
                self.matter,
                self.matter_fabric,
                self.behavior_script,
                self.behavior_instance,
            ],
        )

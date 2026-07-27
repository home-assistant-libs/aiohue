"""
Model(s) for zigbee_device_discovery resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zigbee_device_discovery
"""

from dataclasses import dataclass
from enum import Enum

from .resource import ResourceIdentifier, ResourceTypes


class ZigbeeDeviceDiscoveryStatus(Enum):
    """
    Enum with the possible statuses of the zigbee device discovery service.

    `active` while the bridge is searching for new devices, `ready` otherwise.
    """

    ACTIVE = "active"
    READY = "ready"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return ZigbeeDeviceDiscoveryStatus.UNKNOWN


class SearchActionType(Enum):
    """
    Enum with the search actions that can be triggered on the bridge.

    search: search for new devices to join the zigbee network.
    search_allow_default_link_key: also let devices join that only support the
    default (well known, less secure) zigbee link key.
    """

    SEARCH = "search"
    SEARCH_ALLOW_DEFAULT_LINK_KEY = "search_allow_default_link_key"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return SearchActionType.UNKNOWN


class SearchChannels(Enum):
    """
    Enum with the zigbee channels that a search can cover.

    Ignored by the bridge when the search is not narrowed down by search codes.
    """

    ALL = "all"
    PRIMARY = "primary"


@dataclass
class ZigbeeDeviceDiscoveryAction:
    """
    Represent the search actions supported by the bridge.

    Used by `zigbee_device_discovery` resources.
    """

    action_type_values: list[SearchActionType]


@dataclass
class ZigbeeDeviceDiscoveryActionPut:
    """
    Search action to start with a PUT request.

    Used by `zigbee_device_discovery` resources.
    """

    action_type: SearchActionType
    # search_codes: limits the search to specific devices, max 10 entries.
    # The api reference does not expand the item type of this array.
    search_codes: list[str] | None = None
    search_channels: SearchChannels | None = None


@dataclass
class InstallCode:
    """
    Represent the install code of a single device.

    Used by `zigbee_device_discovery` resources.
    """

    # mac_address: as `AA:BB:CC:DD:EE:FF:00:11`
    mac_address: str
    # ic: the 36 character install code printed on the device or its packaging
    ic: str


@dataclass
class AddInstallCodes:
    """
    Install codes of devices that are allowed to join the network.

    Used by `zigbee_device_discovery` resources. Write-only: the bridge returns
    this object without any properties.
    """

    # install_codes: min 1, max 50 entries
    install_codes: list[InstallCode] | None = None


@dataclass
class ZigbeeDeviceDiscovery:
    """
    Represent a (full) `ZigbeeDeviceDiscovery` resource when retrieved from the api.

    Offered by the bridge to commission new zigbee devices.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zigbee_device_discovery_get
    """

    id: str
    owner: ResourceIdentifier
    status: ZigbeeDeviceDiscoveryStatus

    # NOTE: older bridge firmware omits both `action` and `add_install_codes`
    # even though the api reference marks `action` as required.
    action: ZigbeeDeviceDiscoveryAction | None = None
    add_install_codes: AddInstallCodes | None = None

    type: ResourceTypes = ResourceTypes.ZIGBEE_DEVICE_DISCOVERY


@dataclass
class ZigbeeDeviceDiscoveryPut:
    """
    ZigbeeDeviceDiscovery properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_zigbee_device_discovery__id__put
    """

    action: ZigbeeDeviceDiscoveryActionPut | None = None
    add_install_codes: AddInstallCodes | None = None

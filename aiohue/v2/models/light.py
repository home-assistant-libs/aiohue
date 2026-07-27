"""
Model(s) for Light resource on HUE bridge.

https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light
"""

from dataclasses import dataclass
from enum import Enum

from .feature import (
    AlertFeature,
    AlertFeaturePut,
    ColorFeature,
    ColorFeatureBase,
    ColorTemperatureDeltaFeature,
    ColorTemperatureDeltaFeaturePut,
    ColorTemperatureFeature,
    ColorTemperatureFeatureBase,
    ConfigurationStatus,
    DimmingDeltaFeature,
    DimmingDeltaFeaturePut,
    DimmingFeature,
    DimmingFeatureBase,
    DynamicsFeature,
    DynamicsFeaturePut,
    DynamicStatus,
    EffectsFeature,
    EffectsFeaturePut,
    EffectsV2Feature,
    EffectsV2FeaturePut,
    GradientFeature,
    GradientFeatureBase,
    IdentifyFeature,
    LightGeometryFeature,
    OnFeature,
    PowerUpFeature,
    PowerUpFeaturePut,
    SignalingFeature,
    SignalingFeaturePut,
    TimedEffectsFeature,
    TimedEffectsFeaturePut,
)
from .resource import ResourceIdentifier, ResourceTypes


class LightFunction(Enum):
    """Enum with all possible functions of a light service."""

    FUNCTIONAL = "functional"
    DECORATIVE = "decorative"
    MIXED = "mixed"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return LightFunction.UNKNOWN


@dataclass
class LightMetaData:
    """
    Represent LightMetaData object as used by the Hue api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    # Light archetype Deprecated: use archetype on device level
    archetype: str | None
    name: str
    # function: Function of the lightservice
    function: LightFunction | None = None
    # fixed_mired: A fixed mired value of the white lamp
    fixed_mired: int | None = None


@dataclass
class LightProductData:
    """
    Represent the factory defaults of a light service.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    # name and archetype are only available for devices with multiple lightservices
    name: str | None = None
    archetype: str | None = None
    function: LightFunction | None = None


class LightMode(Enum):
    """
    Enum with all possible LightModes.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    NORMAL = "normal"
    STREAMING = "streaming"


class ContentOrientation(Enum):
    """Enum with possible orientations of content deployed on a light."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return ContentOrientation.UNKNOWN


class ContentOrder(Enum):
    """Enum with possible orders in which content is represented on the pixels."""

    FORWARD = "forward"
    REVERSED = "reversed"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return ContentOrder.UNKNOWN


class ContentAssociation(Enum):
    """
    Enum with the objects a light service can be associated with.

    `screen` means the light is placed behind or around a screen following an arc.
    """

    NOT_ASSOCIATED = "not_associated"
    SCREEN = "screen"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls: type, value: object):  # noqa: ARG003
        """Set default enum member if an unknown value is provided."""
        return ContentAssociation.UNKNOWN


@dataclass
class ContentOrientationConfiguration:
    """Represent the orientation for content deployed on pixelated products."""

    orientation: ContentOrientation = ContentOrientation.UNKNOWN
    status: ConfigurationStatus = ConfigurationStatus.UNKNOWN
    # configurable: Indicates if the product allows modifying this attribute
    configurable: bool = False


@dataclass
class ContentOrderConfiguration:
    """Represent the order in which content is represented on the pixels."""

    order: ContentOrder = ContentOrder.UNKNOWN
    status: ConfigurationStatus = ConfigurationStatus.UNKNOWN
    # configurable: Indicates if the product allows modifying this attribute
    configurable: bool = False


@dataclass
class ContentAssociationConfiguration:
    """Represent what the light service is associated with, e.g. a screen."""

    association: ContentAssociation = ContentAssociation.UNKNOWN


@dataclass
class ContentConfiguration:
    """
    Represent the parameters that affect how content is deployed on a light.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    orientation: ContentOrientationConfiguration | None = None
    order: ContentOrderConfiguration | None = None
    association: ContentAssociationConfiguration | None = None


@dataclass
class Light:
    """
    Represent a (full) `Light` resource when retrieved from the api.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light_get
    """

    # pylint: disable=too-many-instance-attributes

    id: str
    owner: ResourceIdentifier
    on: OnFeature
    mode: LightMode

    id_v1: str | None = None
    metadata: LightMetaData | None = None
    # product_data: Factory defaults of the product data
    product_data: LightProductData | None = None
    # service_id: Service identification number.
    # 0 indicates service of a single instance
    service_id: int | None = None
    identify: IdentifyFeature | None = None
    dimming: DimmingFeature | None = None
    dimming_delta: DimmingDeltaFeature | None = None
    color_temperature: ColorTemperatureFeature | None = None
    color_temperature_delta: ColorTemperatureDeltaFeature | None = None
    color: ColorFeature | None = None
    dynamics: DynamicsFeature | None = None
    alert: AlertFeature | None = None
    signaling: SignalingFeature | None = None
    gradient: GradientFeature | None = None
    effects: EffectsFeature | None = None
    effects_v2: EffectsV2Feature | None = None
    timed_effects: TimedEffectsFeature | None = None
    powerup: PowerUpFeature | None = None
    content_configuration: ContentConfiguration | None = None
    geometry: LightGeometryFeature | None = None

    type: ResourceTypes = ResourceTypes.LIGHT

    @property
    def supports_dimming(self) -> bool:
        """Return if this light supports brightness control."""
        return self.dimming is not None

    @property
    def supports_color(self) -> bool:
        """Return if this light supports color control."""
        return self.color is not None

    @property
    def supports_color_temperature(self) -> bool:
        """Return if this light supports color_temperature control."""
        return self.color_temperature is not None

    @property
    def is_on(self) -> bool:
        """Return bool if light is currently powered on."""
        if self.on is not None:
            return self.on.on
        return False

    @property
    def brightness(self) -> float:
        """Return current brightness of light."""
        if self.dimming is not None:
            return self.dimming.brightness
        return 100.0 if self.is_on else 0.0

    @property
    def is_dynamic(self) -> bool:
        """Return bool if light is currently dynamically changing colors from a scene."""
        if self.dynamics is not None:
            return self.dynamics.status == DynamicStatus.DYNAMIC_PALETTE
        return False

    @property
    def entertainment_active(self) -> bool:
        """Return bool if this light is currently streaming in Entertainment mode."""
        return self.mode == LightMode.STREAMING


@dataclass
class LightPut:
    """
    Light resource properties that can be set/updated with a PUT request.

    https://developers.meethue.com/develop/hue-api-v2/api-reference/#resource_light__id__put
    """

    on: OnFeature | None = None
    dimming: DimmingFeatureBase | None = None
    dimming_delta: DimmingDeltaFeaturePut | None = None
    color_temperature: ColorTemperatureFeatureBase | None = None
    color_temperature_delta: ColorTemperatureDeltaFeaturePut | None = None
    color: ColorFeatureBase | None = None
    dynamics: DynamicsFeaturePut | None = None
    alert: AlertFeaturePut | None = None
    gradient: GradientFeatureBase | None = None
    effects: EffectsFeaturePut | None = None
    effects_v2: EffectsV2FeaturePut | None = None
    timed_effects: TimedEffectsFeaturePut | None = None
    powerup: PowerUpFeaturePut | None = None
    signaling: SignalingFeaturePut | None = None

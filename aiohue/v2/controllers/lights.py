"""Controller holding and managing HUE resources of type `light`."""

from typing import Optional, Tuple, Type, Union

from ..models.feature import (
    AlertEffectType,
    AlertFeaturePut,
    ColorFeaturePut,
    ColorPoint,
    ColorTemperatureFeaturePut,
    DimmingFeaturePut,
    DynamicsFeaturePut,
    EffectsFeaturePut,
    EffectStatus,
    OnFeature,
    TimedEffectStatus,
    TimedEffectsFeaturePut,
)
from ..models.light import Light, LightPut
from ..models.resource import ResourceTypes
from .base import BaseResourcesController


class LightsController(BaseResourcesController[Type[Light]]):
    """Controller holding and managing HUE resources of type `light`."""

    item_type = ResourceTypes.LIGHT
    item_cls = Light

    async def turn_on(self, id: str, transition_time: Optional[int] = None) -> None:
        """Turn on the light."""
        await self.set_state(id, on=True, transition_time=transition_time)

    async def turn_off(self, id: str, transition_time: Optional[int] = None) -> None:
        """Turn off the light."""
        await self.set_state(id, on=False, transition_time=transition_time)

    async def set_brightness(
        self, id: str, brightness: float, transition_time: Optional[int] = None
    ) -> None:
        """Set brightness to light. Turn on light if it's currently off."""
        await self.set_state(
            id, on=True, brightness=brightness, transition_time=transition_time
        )

    async def set_color(
        self, id: str, x: float, y: float, transition_time: Optional[int] = None
    ) -> None:
        """Set color to light. Turn on light if it's currently off."""
        await self.set_state(
            id, on=True, color_xy=(x, y), transition_time=transition_time
        )

    async def set_color_temperature(
        self, id: str, mirek: int, transition_time: Optional[int] = None
    ) -> None:
        """Set Color Temperature to light. Turn on light if it's currently off."""
        await self.set_state(
            id, on=True, color_temp=mirek, transition_time=transition_time
        )

    async def set_flash(self, id: str, short: bool = False) -> None:
        """Send Flash command to light."""
        if short:
            device = self.get_device(id)
            await self._bridge.devices.set_identify(device.id)
        else:
            await self.set_state(id, alert=AlertEffectType.BREATHE)

    async def set_state(
        self,
        id: str,
        on: Optional[bool] = None,
        brightness: Optional[float] = None,
        color_xy: Optional[Tuple[float, float]] = None,
        color_temp: Optional[int] = None,
        transition_time: Optional[int] = None,
        alert: Optional[AlertEffectType] = None,
        effect: Union[EffectStatus, TimedEffectStatus, None] = None,
    ) -> None:
        """Set supported feature(s) to light resource."""
        update_obj = LightPut()
        if on is not None:
            update_obj.on = OnFeature(on=on)
        if brightness is not None:
            update_obj.dimming = DimmingFeaturePut(brightness=brightness)
        if color_xy is not None:
            update_obj.color = ColorFeaturePut(xy=ColorPoint(*color_xy))
        if color_temp is not None:
            update_obj.color_temperature = ColorTemperatureFeaturePut(mirek=color_temp)
        if transition_time is not None and effect is None:
            update_obj.dynamics = DynamicsFeaturePut(duration=transition_time)
        if alert is not None:
            update_obj.alert = AlertFeaturePut(action=alert)

        # for timed_effects feature, transition time is used for duration
        if effect is not None and isinstance(effect, TimedEffectStatus):
            update_obj.timed_effects = TimedEffectsFeaturePut(
                effect=effect, duration=transition_time
            )
        elif effect is not None:
            update_obj.effects = EffectsFeaturePut(effect=effect)
        await self.update(id, update_obj)

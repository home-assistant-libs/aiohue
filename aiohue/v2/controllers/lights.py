"""Controller holding and managing HUE resources of type `light`."""
from __future__ import annotations

from typing import Optional, Tuple, Type

from ..models.feature import (
    AlertEffectType,
    AlertFeature,
    ColorFeature,
    ColorPoint,
    ColorTemperatureFeature,
    DimmingFeature,
    DynamicsFeature,
    OnFeature,
)
from ..models.light import Light
from ..models.resource import ResourceTypes
from .base import BaseResourcesController


class LightsController(BaseResourcesController[Type[Light]]):
    """Controller holding and managing HUE resources of type `light`."""

    item_type = ResourceTypes.LIGHT

    async def turn_on(self, id: str, transition_time: int | None = None) -> None:
        """Turn on the light."""
        await self.set_state(id, on=True, transition_time=transition_time)

    async def turn_off(self, id: str, transition_time: int | None = None) -> None:
        """Turn off the light."""
        await self.set_state(id, on=False, transition_time=transition_time)

    async def set_brightness(
        self, id: str, brightness: float, transition_time: int | None = None
    ) -> None:
        """Set brightness to light. Turn on light if it's currently off."""
        await self.set_state(
            id, on=True, brightness=brightness, transition_time=transition_time
        )

    async def set_color(
        self, id: str, x: float, y: float, transition_time: int | None = None
    ) -> None:
        """Set color to light. Turn on light if it's currently off."""
        await self.set_state(
            id, on=True, color_xy=(x, y), transition_time=transition_time
        )

    async def set_color_temperature(
        self, id: str, mirek: int, transition_time: int | None = None
    ) -> None:
        """Set Color Temperature to light. Turn on light if it's currently off."""
        await self.set_state(
            id, on=True, color_temp=mirek, transition_time=transition_time
        )

    async def set_state(
        self,
        id: str,
        on: bool = True,
        brightness: Optional[float] = None,
        color_xy: Optional[Tuple[float, float]] = None,
        color_temp: Optional[int] = None,
        transition_time: int | None = None,
        alert: AlertEffectType | None = None,
    ) -> None:
        """Set supported feature(s) to light resource."""
        update_obj = Light(id=id, on=OnFeature(on=on))
        if brightness is not None:
            update_obj.dimming = DimmingFeature(brightness=brightness)
        if color_xy is not None:
            update_obj.color = ColorFeature(xy=ColorPoint(*color_xy))
        if color_temp is not None:
            update_obj.color_temperature = ColorTemperatureFeature(mirek=color_temp)
        if transition_time is not None:
            update_obj.dynamics = DynamicsFeature(duration=transition_time)
        if alert is not None:
            update_obj.alert = AlertFeature(action=alert)
        await self.update(id, update_obj)

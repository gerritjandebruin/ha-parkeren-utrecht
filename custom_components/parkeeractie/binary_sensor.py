from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .base import BaseCoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coord = hass.data["parkeeractie"][entry.entry_id]
    async_add_entities([ParkeerProbleemSensor(coord, entry)])


class ParkeerProbleemSensor(BaseCoordinatorEntity, BinarySensorEntity):
    _attr_name = "Parkeerprobleem"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def unique_id(self) -> str:
        return f"{self.entry_id}_parkeren_problem"

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data or {}
        if not data:
            return None  # vóór eerste refresh
        saldo = data.get("saldo") or 0
        current_time = data.get("current_time")
        # PROBLEEM indien: geen geld óf geen tijd (00:00:00 of None)
        no_money = saldo <= 0
        no_time = current_time in (None, "00:00:00")
        return bool(no_money or no_time)

    @property
    def extra_state_attributes(self):
        d = self.coordinator.data or {}
        return {
            "saldo": d.get("saldo"),
            "current_time": d.get("current_time"),
            "reason": (
                "geen_geld"
                if (d.get("saldo") or 0) <= 0
                else (
                    "geen_tijd"
                    if d.get("current_time") in (None, "00:00:00")
                    else "geen"
                )
            ),
        }

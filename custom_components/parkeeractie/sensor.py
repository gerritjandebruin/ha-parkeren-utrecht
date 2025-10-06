from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfTime

from .base import BaseCoordinatorEntity


def _hhmmss_to_seconds(raw: str | None) -> int | None:
    if not isinstance(raw, str) or raw.count(":") != 2:
        return None
    try:
        h, m, s = (int(x) for x in raw.split(":"))
        return h * 3600 + m * 60 + s
    except Exception:
        return None


async def async_setup_entry(hass, entry, add_entities) -> None:
    coordinator = hass.data["parkeeractie"][entry.entry_id]
    add_entities(
        [
            SaldoSensor(coordinator, entry),
            TimeRemainingSensor(coordinator, entry),
        ]
    )


class SaldoSensor(BaseCoordinatorEntity, SensorEntity):
    _attr_name = "Saldo"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "EUR"
    _attr_suggested_display_precision = 2

    @property
    def unique_id(self) -> str:
        return f"{self.entry_id}_saldo"

    @property
    def native_value(self):
        return self.coordinator.data.get("saldo")


class TimeRemainingSensor(BaseCoordinatorEntity, SensorEntity):
    _attr_name = "Tijd resterend"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_icon = "mdi:timer-outline"

    @property
    def unique_id(self) -> str:
        return f"{self.entry_id}_time_remaining"

    @property
    def native_value(self):
        raw = self.coordinator.data.get("current_time")
        secs = _hhmmss_to_seconds(raw)
        # Als tijd n.v.t. is, rapporteer 0 uren (en attribuut geeft n.v.t. aan)
        if secs is None:
            return 0
        # Convert seconds to hours (rounded to 2 decimal places)
        return round(secs / 3600, 2)

    @property
    def extra_state_attributes(self):
        raw = self.coordinator.data.get("current_time")
        secs = _hhmmss_to_seconds(raw)
        not_applicable = secs is None
        if not_applicable:
            secs = 0
        return {
            "raw": raw or "00:00:00",
            "time_applicable": not not_applicable,
            "display_format": raw or "00:00:00",
        }

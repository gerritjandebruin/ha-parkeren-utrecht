"""Sensor entities for Parkeeractie integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfTime

from .base import BaseCoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Constants
TIME_FORMAT_PARTS = 3  # Expected number of parts in HH:MM:SS format


def _hhmmss_to_seconds(raw: str | None) -> int | None:
    """Convert HH:MM:SS string to seconds."""
    if not isinstance(raw, str) or raw.count(":") != TIME_FORMAT_PARTS - 1:
        return None
    try:
        h, m, s = (int(x) for x in raw.split(":"))
        return h * 3600 + m * 60 + s
    except (ValueError, TypeError):
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator = hass.data["parkeeractie"][entry.entry_id]
    add_entities(
        [
            SaldoSensor(coordinator, entry),
            TimeRemainingSensor(coordinator, entry),
        ]
    )


class SaldoSensor(BaseCoordinatorEntity, SensorEntity):
    """Sensor showing parking account balance."""

    _attr_name = "Saldo"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "EUR"
    _attr_suggested_display_precision = 2

    @property
    def unique_id(self) -> str:
        """Return unique ID for this sensor."""
        return f"{self.entry_id}_saldo"

    @property
    def native_value(self) -> float | None:
        """Return the current balance."""
        return self.coordinator.data.get("saldo")


class TimeRemainingSensor(BaseCoordinatorEntity, SensorEntity):
    """Sensor showing remaining parking time."""

    _attr_name = "Tijd resterend"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_icon = "mdi:timer-outline"

    @property
    def unique_id(self) -> str:
        """Return unique ID for this sensor."""
        return f"{self.entry_id}_time_remaining"

    @property
    def native_value(self) -> float | None:
        """Return remaining time in hours."""
        raw = self.coordinator.data.get("current_time")
        secs = _hhmmss_to_seconds(raw)
        # Als tijd n.v.t. is, rapporteer 0 uren (en attribuut geeft n.v.t. aan)
        if secs is None:
            return 0
        # Convert seconds to hours (rounded to 2 decimal places)
        return round(secs / 3600, 2)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
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

"""The Parkeren Utrecht integration."""

from __future__ import annotations

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ParkeeractieClient
from .coordinator import ParkeeractieConfigEntry, ParkeeractieCoordinator

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, entry: ParkeeractieConfigEntry
) -> bool:
    """Set up an account from a config entry."""
    if entry.unique_id is None:
        # Entries from before 1.2.0 have no unique_id.
        hass.config_entries.async_update_entry(
            entry, unique_id=entry.data[CONF_USERNAME].strip().lower()
        )
    client = ParkeeractieClient(
        async_get_clientsession(hass),
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )
    coordinator = ParkeeractieCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ParkeeractieConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

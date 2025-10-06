from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ParkeeractieClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ParkeeractieCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, username: str, password: str):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._session = async_get_clientsession(hass)
        self._client = ParkeeractieClient(self._session, username, password)

    @property
    def client(self) -> ParkeeractieClient:
        """Get the API client for service calls."""
        return self._client

    async def _async_update_data(self):
        try:
            saldo, current_time = await self._client.login_and_fetch()
            return {"saldo": saldo, "current_time": current_time}
        except Exception as err:
            raise UpdateFailed(str(err)) from err

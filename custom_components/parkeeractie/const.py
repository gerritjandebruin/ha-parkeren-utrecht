"""Constants for the Parkeren Utrecht integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "parkeeractie"

BASE_URL: Final = "https://parkeerapp.utrecht.nl"
LOGIN_URL: Final = f"{BASE_URL}/"

UPDATE_INTERVAL: Final = timedelta(minutes=5)

HEADERS: Final = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "nl-NL,nl;q=0.9,en;q=0.8",
}

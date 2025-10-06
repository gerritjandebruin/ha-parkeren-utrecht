"""Constants for Parkeeractie integration."""

DOMAIN = "parkeeractie"
BASE_URL = "https://parkeerapp.utrecht.nl"
LOGIN_URL = f"{BASE_URL}/"
PLAN_URL = f"{BASE_URL}/Customer/PlanSession/Index/"

DEFAULT_SCAN_INTERVAL = 300  # 5 min
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "nl-NL,nl;q=0.9,en;q=0.8",
}

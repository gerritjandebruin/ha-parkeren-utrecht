"""API client for Parkeeractie Utrecht parking service."""

from __future__ import annotations

import contextlib
import html as ihtml
import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from .const import BASE_URL, HEADERS, LOGIN_URL, PLAN_URL

_LOGGER = logging.getLogger(__name__)

_login_payload_re = re.compile(
    r"login\.init\(\s*(['\"])(?P<payload>.+?)\1\)\s*;", re.DOTALL
)
_customer_payload_re = re.compile(
    r"customerLayout\.init\([^,]+,\s*(['\"])(?P<payload>.+?)\1\)\s*;", re.DOTALL
)

_DEFAULT_TZ = ZoneInfo("Europe/Amsterdam")


def _format_utc(dt: datetime) -> str:
    """Return an ISO string with millisecond precision and Z suffix."""
    dt_utc = dt.astimezone(UTC).replace(microsecond=0)
    return f"{dt_utc.strftime('%Y-%m-%dT%H:%M:%S')}.000Z"


def _load_relaxed(s: str) -> dict:
    """
    Parse JSON that may be HTML-escaped or lightly malformed.

    Tries a couple of safe variants before finally attempting a unicode_escape decode.
    Avoids logging for each failed candidate to reduce noise; logs once on the final
    fallback.
    """
    s1 = ihtml.unescape(s)
    candidates = (
        s1,
        s1.replace(r"\\", "\\").replace(r"\"", '"').replace(r"\'", "'"),
    )
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except (ValueError, json.JSONDecodeError):
            # Silent per-candidate failure; we'll try the next strategy.
            continue
    try:
        return json.loads(s1.encode("utf-8").decode("unicode_escape"))
    except (ValueError, json.JSONDecodeError) as e:
        _LOGGER.debug("Relaxed JSON parse fallback failed: %s", e)
        raise


def _ensure_www() -> str:
    """Ensure www directory exists and return its path."""
    www_dir = "config/www"
    with contextlib.suppress(Exception):
        Path(www_dir).mkdir(parents=True, exist_ok=True)
    return www_dir


class ParkeeractieClient:
    """Client for interacting with the Parkeeractie Utrecht API."""

    def __init__(self, session: ClientSession, username: str, password: str) -> None:
        """Initialize the client with session and credentials."""
        self._session = session
        self._username = username
        self._password = password

    async def _get(self, url: str) -> str:
        async with self._session.get(url, headers=HEADERS, allow_redirects=True) as r:
            text = await r.text()
            _LOGGER.debug("GET %s -> %s (%s)", url, str(r.url), r.status)
            return text

    async def _post_form(self, url: str, data: dict, referer: str) -> str:
        headers = {**HEADERS, "Referer": referer}
        async with self._session.post(
            url, headers=headers, data=data, allow_redirects=True
        ) as r:
            text = await r.text()
            _LOGGER.debug("POST %s -> %s (%s)", url, str(r.url), r.status)
            return text

    async def _post_json(
        self, url: str, data: dict, referer: str, extra_headers: dict | None = None
    ) -> str:
        headers = {
            **HEADERS,
            "Referer": referer,
            "Origin": BASE_URL,
            "Content-Type": "application/json; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        }
        if extra_headers:
            headers.update(extra_headers)
        async with self._session.post(
            url, headers=headers, json=data, allow_redirects=True
        ) as r:
            text = await r.text()
            _LOGGER.debug("POST JSON %s -> %s (%s)", url, str(r.url), r.status)
            return text

    async def login_and_fetch(self) -> tuple[float | None, str | None]:
        """Login to the service and fetch saldo and current time data."""
        # 1) GET "/" - can be login or already logged in
        html = await self._get(LOGIN_URL)

        # a) Als we al ingelogd zijn, staat de payload direct in de pagina
        saldo, current_time = self._parse_saldo_and_time(html)
        if saldo is not None or current_time is not None:
            # We waren al ingelogd; niets posten, meteen teruggeven
            return saldo, current_time

        # b) Geen ingelogde payload? Probeer expliciete login-URL
        if "login.init" not in html.lower():
            alt_url = f"{BASE_URL}/Account/Login"
            html = await self._get(alt_url)

        m = _login_payload_re.search(html)
        if not m:
            # Laatste kans: misschien staat de payload alsnog in deze pagina
            saldo, current_time = self._parse_saldo_and_time(html)
            if saldo is not None or current_time is not None:
                return saldo, current_time

            # Nog steeds geen login/init en geen ingelogde payload -> debugdump + error
            path = Path(_ensure_www()) / "parkeeractie_login_debug.html"
            try:
                path.write_text(html, encoding="utf-8")
                _LOGGER.error(
                    "Kon login.init payload niet vinden. "
                    "HTML opgeslagen naar %s "
                    "(open via /local/parkeeractie_login_debug.html)",
                    path,
                )
            except Exception:
                _LOGGER.exception("Kon debug HTML niet schrijven")
            msg = "Kon login.init payload niet vinden."
            raise ValueError(msg)

        # 2) CSRF + captcha check
        soup = BeautifulSoup(html, "html.parser")
        token_el = soup.find("input", {"name": "__RequestVerificationToken"})
        if not token_el or not token_el.get("value"):
            msg = "CSRF-token niet gevonden op loginpagina."
            raise ValueError(msg)
        csrf = token_el["value"]

        login_payload = _load_relaxed(m.group("payload"))
        show_captcha = bool(
            login_payload.get("showCaptcha") or login_payload.get("ShowCaptcha")
        )
        if show_captcha:
            msg = "reCAPTCHA staat aan (showCaptcha=true) — inloggen afgebroken."
            raise ValueError(msg)

        # 3) POST credentials
        form_data = {
            "__RequestVerificationToken": csrf,
            "Email": self._username,
            "Password": self._password,
            "ReturnUrl": login_payload.get("returnUrl", "") or "",
            "ShowCaptcha": "False",
            "ScreenWidth": "1920",
        }

        html = await self._post_form(LOGIN_URL, form_data, LOGIN_URL)
        saldo, current_time = self._parse_saldo_and_time(html)
        if saldo is not None or current_time is not None:
            return saldo, current_time
        msg = "Inloggen is mislukt of geen account gevonden."
        raise ValueError(msg)

    def _parse_saldo_and_time(self, html: str) -> tuple[float | None, str | None]:
        payload = None
        if m := _customer_payload_re.search(html):
            try:
                payload = _load_relaxed(m.group("payload"))
            except (json.JSONDecodeError, UnicodeError) as e:
                _LOGGER.debug(
                    "Payload parse error (%s): %s", _customer_payload_re.pattern, e
                )

        saldo = None
        current_time = None
        if payload:
            if isinstance(payload.get("addItem"), dict):
                add = payload["addItem"]

                if isinstance(add.get("saldo"), (int, float)):
                    saldo = float(add["saldo"])

                # Look for time from addItem first (active session)
                current_time = (
                    add.get("timeRemaining")
                    or add.get("currentTime")
                    or add.get("remainingTime")
                    or add.get("tijd")
                    or add.get("tijdResterend")
                    or add.get("restTime")
                )

                # If no active session time, check permit time balance
                if current_time is None and isinstance(payload.get("permitList"), list):
                    for permit in payload["permitList"]:
                        if (
                            isinstance(permit, dict)
                            and permit.get("status") == "Active"
                        ):
                            time_balance = permit.get("timeBalance")
                            if (
                                isinstance(time_balance, (int, float))
                                and time_balance > 0
                            ):
                                # Convert minutes to HH:MM:SS format
                                minutes = int(time_balance)
                                hours = minutes // 60
                                remaining_minutes = minutes % 60
                                current_time = f"{hours:02d}:{remaining_minutes:02d}:00"
                                _LOGGER.debug(
                                    "Using permit timeBalance: %d minutes -> %s",
                                    time_balance,
                                    current_time,
                                )
                                break

                _LOGGER.debug("Selected current_time: %s", current_time)
            else:
                _LOGGER.debug(
                    "No addItem found or not a dict. Payload keys: %s",
                    list(payload.keys()) if isinstance(payload, dict) else "Not a dict",
                )
        return saldo, current_time

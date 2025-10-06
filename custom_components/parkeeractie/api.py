from __future__ import annotations

import contextlib
import html as ihtml
import json
import logging
import os
import re
from datetime import UTC, datetime

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
_plan_payload_re = re.compile(
    r"planSession\.init\(\s*(['\"])(?P<payload>.+?)\1\)\s*;", re.DOTALL
)


def _load_relaxed(s: str) -> dict:
    s1 = ihtml.unescape(s)
    for candidate in (
        s1,
        s1.replace(r"\\", "\\").replace(r"\"", '"').replace(r"\'", "'"),
    ):
        try:
            return json.loads(candidate)
        except Exception:
            pass
    return json.loads(s1.encode("utf-8").decode("unicode_escape"))


def _ensure_www():
    www_dir = "/config/www"
    with contextlib.suppress(Exception):
        os.makedirs(www_dir, exist_ok=True)
    return www_dir


class ParkeeractieClient:
    def __init__(self, session: ClientSession, username: str, password: str) -> None:
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

    async def _post_json(self, url: str, data: dict, referer: str) -> str:
        headers = {
            **HEADERS,
            "Referer": referer,
            "Origin": BASE_URL,
            "Content-Type": "application/json; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
        }
        async with self._session.post(
            url, headers=headers, json=data, allow_redirects=True
        ) as r:
            text = await r.text()
            _LOGGER.debug("POST JSON %s -> %s (%s)", url, str(r.url), r.status)
            return text

    async def login_and_fetch(self) -> tuple[float | None, str | None]:
        # 1) GET "/" – kan óf login óf al ingelogd zijn
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

            # Nog steeds geen login/init en geen ingelogde payload → debugdump + error
            path = os.path.join(_ensure_www(), "parkeeractie_login_debug.html")
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(html)
                _LOGGER.error(
                    "Kon login.init payload niet vinden. HTML opgeslagen naar %s (open via /local/parkeeractie_login_debug.html)",
                    path,
                )
            except Exception as e:
                _LOGGER.exception("Kon debug HTML niet schrijven: %s", e)
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
        # 4) Nog geen payload? Probeer plan-URL
        html = await self._get(PLAN_URL)
        saldo, current_time = self._parse_saldo_and_time(html)
        if saldo is not None or current_time is not None:
            return saldo, current_time
        msg = "Inloggen is mislukt of geen account gevonden."
        raise ValueError(msg)

    def _parse_saldo_and_time(self, html: str) -> tuple[float | None, str | None]:
        payload = None
        for regex in (_customer_payload_re, _plan_payload_re):
            m = regex.search(html)
            if m:
                try:
                    payload = _load_relaxed(m.group("payload"))
                    break
                except (json.JSONDecodeError, UnicodeError) as e:
                    _LOGGER.debug("Payload parse error (%s): %s", regex.pattern, e)

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

    async def start_parking_session(self, license_plate: str, end_time: str) -> bool:
        """
        Start een parkeerssessie voor een kenteken tot een bepaalde tijd.

        Args:
            license_plate: Het kenteken (bijv. "AB-123-CD")
            end_time: Eindtijd in ISO format (bijv. "2025-10-06T23:00:00")

        Returns:
            True als de sessie succesvol is gestart, False anders

        """
        try:
            # 1) Fresh login voor de parkeerssessie
            _LOGGER.debug("Starting fresh login for parking session")
            await self.login_and_fetch()

            # 2) Verkrijg verse plan session pagina voor CSRF token
            _LOGGER.debug("Fetching fresh plan session page")
            html = await self._get(PLAN_URL)

            # Check if we're actually logged in (look for user data)
            if "userDisplayName" not in html:
                _LOGGER.error("Not properly logged in - no user data found")
                return False

            # Parse CSRF token
            soup = BeautifulSoup(html, "html.parser")
            token_el = soup.find("input", {"name": "__RequestVerificationToken"})
            if not token_el or not token_el.get("value"):
                msg = "CSRF-token niet gevonden op plan session pagina."
                raise ValueError(msg)
            token_el["value"]

            # Parse plan session payload
            payload = None
            for regex in (_customer_payload_re, _plan_payload_re):
                m = regex.search(html)
                if m:
                    try:
                        payload = _load_relaxed(m.group("payload"))
                        break
                    except (json.JSONDecodeError, UnicodeError) as e:
                        _LOGGER.debug("Payload parse error (%s): %s", regex.pattern, e)

            if not payload:
                msg = "Kon plan session payload niet vinden."
                raise ValueError(msg)

            # 3) Vind de juiste permit
            permit_list = payload.get("permitList", [])
            if not permit_list:
                msg = "Geen parkeerproducten gevonden."
                raise ValueError(msg)

            selected_permit = None
            # Gebruik eerste actieve permit
            for permit in permit_list:
                if permit.get("status") == "Active":
                    selected_permit = permit
                    break
            if not selected_permit:
                msg = "Geen actieve parkeerproducten gevonden."
                raise ValueError(msg)

            # 4) Bouw sessie data voor form POST
            # Controleer of de end_time al een datetime object is of string
            if isinstance(end_time, str) and "T" in end_time:
                # ISO format datetime string, mogelijk aanpassen voor parkeerapp
                try:
                    dt = datetime.fromisoformat(end_time)
                    # Parkeerapp verwacht mogelijk lokale tijd
                    formatted_time = dt.strftime("%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    formatted_time = end_time
            else:
                formatted_time = str(end_time)

            # 4) Bereid JSON data voor (zoals browser - uitgebreide payload)
            # Genereer UTC timestamps in juiste formaat (.000Z)
            start_time = datetime.now(UTC)

            # Format end time correctly (.000Z suffix)
            if "+00:00" in formatted_time:
                end_time_formatted = formatted_time.replace("+00:00", ".000Z")
            else:
                end_time_formatted = f"{formatted_time}.000Z"

            # Use realistic parking regime times (9 AM to 11 PM local time)
            today = start_time.replace(hour=9, minute=0, second=0, microsecond=0)
            regime_end = start_time.replace(hour=23, minute=0, second=0, microsecond=0)

            session_data = {
                "parkingSessionId": 0,
                "permitId": selected_permit["id"],
                "timeStartUtc": start_time.strftime("%Y-%m-%dT%H:%M:00.000Z"),
                "timeEndUtc": end_time_formatted,
                "statusId": 0,
                "untilType": None,
                "costMoney": None,
                "costTime": None,
                "parkingRegime": None,
                "hourRate": None,
                "lp": license_plate.upper().replace("-", ""),
                "psRightId": None,
                "garageCode": None,
                "startTimeNow": False,  # False omdat we expliciete tijden geven
                "endTimeParkingRegimeEnd": False,
                "saveMode": True,
                "newEndTimeString": None,
                "moneyBalance": 0.0,
                "moneyRemaining": None,
                "timeRemaining": None,
                "timeCostString": None,
                "costTimeHours": "00:00:00",
                "overMoneyLimit": False,
                "overMoneyLimitText": None,
                "overTimeLimit": False,
                "overTimeLimitText": None,
                "insufficientResources": False,
                "insufficientResourcesText": None,
                "unixDateTime": 0.0,
                "regimeEndTime": regime_end.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
                "regimeStartTime": today.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
                "permitProductId": selected_permit.get("permitProductId", 33),
                "canAddLp": True,
                "currentMoney": None,
                "currentTime": None,
                "balanceResetTime": "",
                "paidRegimePeriodMessage": "",
                "garageSessionMessage": "",
                "isUnlimitedPermit": False,
                "overSessionHourLimit": False,
                "overSessionHourLimitText": None,
                "gapNotPassed": False,
                "gapTooShortMessage": None,
                "endTimeAdjusted": False,
                "endTimeAdjustedText": None,
                "maxStartEndSessionSpanOverLimit": False,
                "maxStartEndSessionSpanOverLimitText": None,
                "isUnlimitedTime": False,
                "planSessionMoneyColumnVisible": False,
                "activePermitsCount": 1,
                "editMode": False,
                "saldo": 0.0,
                "isPermitOwner": True,
                "startedForUser": 31195,
                "currentPermitId": selected_permit["id"],
                "customerPays": True,
                "garageId": 0,
            }

            _LOGGER.debug("Sending parking session JSON data: %s", session_data)

            # Debug: Log current cookies
            cookies = {cookie.key: cookie.value for cookie in self._session.cookie_jar}
            _LOGGER.debug("Current cookies: %s", list(cookies.keys()))

            # 5) Start de parkeerssessie met JSON POST (zoals browser)
            save_url = f"{BASE_URL}/Customer/PlanSession/StartParkingSession"
            response = await self._post_json(save_url, session_data, PLAN_URL)

            # Debug: Log de response om te zien wat we krijgen
            _LOGGER.debug("StartParkingSession response: %s", response[:1000])

            # 6) Parse JSON response
            try:
                result = json.loads(response)
                if result.get("successful", False):
                    _LOGGER.info(
                        "Parkeerssessie succesvol gestart voor %s tot %s",
                        license_plate,
                        end_time,
                    )
                    return True

                # Fout - log de notificaties
                notifications = result.get("notifications", [])
                if notifications:
                    for notification in notifications:
                        message = notification.get("message", "Onbekende fout")
                        _LOGGER.error(
                            "Parkeerssessie starten mislukt voor %s: %s",
                            license_plate,
                            message,
                        )
                else:
                    _LOGGER.error(
                        "Parkeerssessie starten mislukt voor %s: %s",
                        license_plate,
                        result,
                    )
                return False

            except json.JSONDecodeError:
                _LOGGER.exception(
                    "Ongeldig JSON antwoord bij starten parkeerssessie: %s",
                    response[:200],
                )
                return False

        except (TimeoutError, aiohttp.ClientError):
            _LOGGER.exception("Network fout bij starten parkeerssessie")
            return False

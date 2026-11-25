# Parkeren Utrecht for Home Assistant

Balance and remaining parking time of your account in the [Utrecht parking app](https://parkeerapp.utrecht.nl).

## What you get

One device per account, with:

- **Balance**: the balance of the parking account in euros.
- **Time remaining**: the remaining time of the active session or, without one, of the active permit, in hours.
- **Parking problem**: on when there is no balance or no time left. The attribute `reason` says which (`geen_geld`, `geen_tijd` or `geen`).

The integration logs in every five minutes and reads the account overview.

## Installation

In Home Assistant: **HACS → Custom repositories**, add `https://github.com/gerritjandebruin/ha-parkeren-utrecht` as an integration and install. Restart, then add the integration under **Settings → Devices & services → Add integration → Parkeren Utrecht** and log in with the email address and password of the parking app.

Manually: copy `custom_components/parkeeractie` into your `config/custom_components/` and restart.

## Notes

- The app has no public API; the integration reads the web pages. A change on the website can break it.
- When the website asks for a reCAPTCHA, logging in fails until it stops asking.
- This integration is not affiliated with the municipality of Utrecht.

## License

MIT

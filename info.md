# Parkeren Utrecht Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This integration allows you to monitor your Parkeeractie Utrecht parking account in Home Assistant.

## Features

- 💰 Monitor your parking account balance
- ⏱️ Track remaining parking time
- 🚗 Start parking sessions directly from Home Assistant
- 🔔 Get notifications about parking issues

## Installation

### Via HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Parkeren Utrecht" in HACS
3. Click Install
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/parkeeractie` folder to your `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Parkeeractie"
4. Enter your Parkeeractie Utrecht credentials

## Services

### `parkeeractie.start_parking_session`

Start a parking session for a specific license plate.

**Parameters:**
- `license_plate` (required): License plate (e.g., "AB-123-CD")
- `end_time` (required): End time for the parking session **in UTC**

**Example:**
```yaml
service: parkeeractie.start_parking_session
data:
  license_plate: "AB123CD"
  end_time: "2025-10-06T18:00:00"
```

## Sensors

- **Saldo**: Current balance in your parking account (€)
- **Tijd resterend**: Remaining parking time (hours)
- **Parkeerprobleem**: Binary sensor indicating if there are any parking issues

## Support

For issues, questions, or feature requests, please [open an issue on GitHub](https://github.com/gerritjandebruin/ha-parkeren-utrecht/issues).

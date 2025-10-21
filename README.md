# Home Assistant Parkeeractie Utrecht

This Home Assistant integration lets you retrieve parking information from the Parkeeractie Utrecht app and start parking sessions directly from Home Assistant.

## Features

### Sensors
- **Balance**: Shows the current balance of your parking account
- **Time Remaining**: Shows the remaining allowance of your parking permit (in hours)

### Binary Sensors
- **Parking Issue**: Indicates whether there is a parking issue (for example, no balance or remaining time)

## Installation

1. Copy the `parkeeractie` folder to your `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for “Parkeeractie” and add the integration
5. Enter your Parkeeractie login credentials

## Configuration

After installation the sensors are available automatically.

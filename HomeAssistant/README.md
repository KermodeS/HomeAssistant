# Home Assistant Modular Automation System

This is a modular automation system for Home Assistant that allows easy enabling/disabling of features and simple maintenance of code.

## Directory Structure

```
/config/python_scripts/
├── common/               # Shared utilities
├── debug/                # Debug utilities
├── services/             # Main functional modules
├── run.py                # Main script to run enabled features
└── feature_flags.yaml    # Feature flag configuration
```

## Feature Flags

The system uses a YAML-based feature flag system to enable or disable specific features. Edit `/config/python_scripts/feature_flags.yaml` to control which features are active.

Example:
```yaml
weather:
  enabled: true           # Master switch for all weather features
  daily_forecast: true    # Daily temperature forecast
  extreme_weather_alert: true # Notifications for rain, wind, snow

grocy:
  enabled: true           # Master switch for Grocy integration
```

## Available Modules

### Weather Module

Processes weather data and sends notifications about:
- Daily temperature forecasts
- Extreme weather alerts (rain, wind, snow)

### Grocy Module

Integrates with Grocy to:
- Check for upcoming chores
- Send formatted notifications with details

### Devices Module

Monitors device status and sends notifications:
- Shelly Caldaia relay state changes

## Debug Tools

The system includes several debug utilities:

- `debug/grocy_debug.py`: Tests Grocy connectivity and endpoints
- `debug/telegram_debug.py`: Tests Telegram messaging

## How to Run

### From Home Assistant

The system is integrated with Home Assistant through shell commands and can be triggered via:
- Automations
- Scripts
- Services

### Manual Execution

You can run modules directly from the command line:

```bash
# Run Grocy module
python3 /config/python_scripts/run.py --mode grocy --hass-token "YOUR_TOKEN" --grocy-url "YOUR_URL" --grocy-api-key "YOUR_KEY"

# Run Weather module
python3 /config/python_scripts/run.py --mode weather --hass-token "YOUR_TOKEN"

# Debug Grocy
python3 /config/python_scripts/debug/grocy_debug.py "YOUR_URL" "YOUR_KEY" "endpoints"
```

## Extending the System

To add a new feature:

1. Create a new module in the `services/` directory
2. Add appropriate feature flags in `feature_flags.yaml`
3. Import and integrate the module in `run.py`
4. Add necessary shell commands in Home Assistant
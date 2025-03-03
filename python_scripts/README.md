# Home Assistant Modular Automation System

## Overview

This is a modular Python-based automation system for Home Assistant that handles various tasks including:

- **Grocy Integration**: Fetches chores and sends notifications
- **Weather Forecasting**: Provides temperature forecasts and extreme weather alerts
- **Device Monitoring**: Tracks device status changes (e.g., Shelly relay switches)

The system is designed to be:

- **Modular**: Each functionality is in its own file/module
- **Configurable**: Features can be enabled/disabled via a central configuration file
- **Extensible**: New modules can be added without changing existing ones
- **Self-healing**: Contains debugging tools to troubleshoot issues

## Directory Structure

```
/config/python_scripts/
├── common/               # Common utilities
│   ├── __init__.py
│   ├── config_manager.py # Configuration management
│   ├── logger.py         # Logging functionality
│   └── notification.py   # Notification services (Telegram)
├── services/             # Service modules
│   ├── __init__.py
│   ├── grocy.py          # Grocy integration
│   ├── weather.py        # Weather forecasting
│   └── devices.py        # Device monitoring
├── debug/                # Debugging tools
│   ├── __init__.py
│   ├── grocy_debug.py    # Grocy API testing
│   ├── telegram_debug.py # Telegram notification testing
│   └── weather_debug.py  # Weather API testing
├── feature_flags.yaml    # Feature configuration
├── run.py                # Main entry point
├── run_wrapper.sh        # Shell wrapper
├── diagnose.py           # System diagnostics
└── token_reader.py       # Token reading utility
```

## Main Components

### 1. Core Files

#### `/config/python_scripts/run.py`
The main entry point for all automation tasks. It processes command-line arguments and calls the appropriate service module.

**Purpose**: Centralizes execution and handles command-line arguments
**Modification**: Add new command-line options when adding new modules

#### `/config/python_scripts/feature_flags.yaml`
Configuration file that enables/disables features.

**Purpose**: Provides centralized control over which features are active
**Modification**: Add new sections when adding new features or modules

#### `/config/python_scripts/run_wrapper.sh`
Shell script that sets up the Python environment and calls run.py.

**Purpose**: Ensures correct PYTHONPATH and handles log redirection
**Modification**: Update if you need special environment variables or paths

### 2. Common Utilities

#### `/config/python_scripts/common/config_manager.py`
Manages feature flags and configuration.

**Purpose**: Reads feature_flags.yaml and provides access to configuration values
**Modification**: Update if you need more sophisticated configuration handling

#### `/config/python_scripts/common/logger.py`
Provides logging functionality.

**Purpose**: Creates consistent logs across all modules
**Modification**: Enhance for log rotation or additional logging destinations

#### `/config/python_scripts/common/notification.py`
Handles sending notifications via Telegram.

**Purpose**: Centralizes notification logic
**Modification**: Add new notification methods (email, push, etc.)

### 3. Service Modules

#### `/config/python_scripts/services/grocy.py`
Fetches chores from Grocy API and sends notifications.

**Purpose**: Integration with Grocy chore management
**Modification**: Add support for shopping lists, inventory, etc.

#### `/config/python_scripts/services/weather.py`
Gets weather forecasts and sends notifications.

**Purpose**: Provides weather alerts and forecasts
**Modification**: Add additional weather metrics or sources

#### `/config/python_scripts/services/devices.py`
Monitors device state changes and sends notifications.

**Purpose**: Notifies about important device changes (e.g., Shelly relay)
**Modification**: Add support for more devices and device types

### 4. Debug Tools

#### `/config/python_scripts/debug/grocy_debug.py`
Tests Grocy API connection and endpoints.

**Purpose**: Helps diagnose Grocy connection issues
**Modification**: Update if Grocy API changes

#### `/config/python_scripts/debug/telegram_debug.py`
Tests Telegram messaging functionality.

**Purpose**: Verifies Telegram notifications are working
**Modification**: Update if notification needs change

#### `/config/python_scripts/debug/weather_debug.py`
Tests weather API connection and data.

**Purpose**: Helps diagnose weather data retrieval issues
**Modification**: Update if weather API changes

#### `/config/python_scripts/diagnose.py`
Comprehensive system diagnosis tool.

**Purpose**: Checks all aspects of the automation system
**Modification**: Update when adding new modules to include them in diagnostics

### 5. Home Assistant Configuration

#### `/config/shell_command.yaml`
Defines shell commands that Home Assistant can execute.

**Purpose**: Enables calling automation scripts from Home Assistant
**Modification**: Add new commands when adding new functionality

#### `/config/scripts.yaml`
Defines Home Assistant scripts that use the shell commands.

**Purpose**: Provides a way to manually trigger automations
**Modification**: Add new scripts for new functionality

#### `/config/automations.yaml`
Defines automations that trigger the scripts.

**Purpose**: Automatically triggers scripts based on events/time
**Modification**: Add new automations when adding new triggers

## Configuration

### Feature Flags

The `feature_flags.yaml` file controls which features are enabled:

```yaml
weather:
  enabled: true  # Master switch for all weather features
  daily_forecast: true  # Daily temperature forecast
  extreme_weather_alert: true  # Notifications for rain, wind, snow

devices:
  enabled: true  # Master switch for all device monitoring
  shelly_caldaia_notifications: true  # Shelly relay status notifications

grocy:
  enabled: true  # Master switch for Grocy integration
  chores_notification: true  # Daily chores notifications

notifications:
  telegram_enabled: true  # Enable/disable all Telegram notifications
  log_to_file: true  # Log notifications to file for debugging

debug:
  verbose_logging: true  # Enable detailed logging
```

To disable a feature, set its value to `false`.

## Adding New Features

To add a new feature:

1. Create a new module in the appropriate directory (usually `/config/python_scripts/services/`)
2. Add the module to `feature_flags.yaml`
3. Update `run.py` to handle the new module
4. Add shell commands to `shell_command.yaml`
5. Add scripts to `scripts.yaml` (optional)
6. Add automations to `automations.yaml` (optional)

## Troubleshooting

### Logs

Log files are stored in `/config/www/logs/`:

- `main.log`: Main application log
- `grocy.log`: Grocy-specific logs
- `weather.log`: Weather-specific logs
- `devices.log`: Device monitoring logs
- `wrapper.log`: Wrapper script logs

### Debug Scripts

Run debug scripts to identify specific issues:

- `/config/python_scripts/debug/grocy_debug.py`: Test Grocy connection
- `/config/python_scripts/debug/telegram_debug.py`: Test Telegram notifications
- `/config/python_scripts/debug/weather_debug.py`: Test weather data retrieval
- `/config/python_scripts/diagnose.py`: Run comprehensive diagnostics

## Maintenance

### Regular Tasks

1. **Log Rotation**: Periodically clear old logs
2. **Configuration Backups**: Backup your configuration files
3. **API Credentials**: Ensure API keys and tokens remain valid
4. **Version Updates**: Update code when Home Assistant APIs change

### Common Issues

- **Shell Command Errors**: Check `returncode` and stderr output
- **API Connection Failures**: Use debug scripts to verify connections
- **Missing Data**: Check entity names and API responses
- **Notification Failures**: Use telegram_debug.py to verify notification path

## Extending the System

When adding new modules:
1. Follow the existing module structure
2. Add comprehensive logging
3. Create debug/test scripts
4. Update feature_flags.yaml
5. Document new features

## Credits

This modular automation system was created for Home Assistant Green to provide a flexible and maintainable approach to automations.
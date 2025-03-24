# Home Assistant Modular Automation System

This is a modular automation system for Home Assistant that allows easy enabling/disabling of features and simple maintenance of code.

# Home Assistant Modular Automation System

## Overview

This is a modular Python-based automation system for Home Assistant that handles various tasks including:

- **Grocy Integration**: Fetches chores and sends notifications
- **Weather Forecasting**: Provides temperature forecasts and extreme weather alerts
- **Device Monitoring**: Tracks device status changes (e.g., Shelly relay switches)
- **Voltage Monitoring**: Monitors voltage levels and sends alerts when thresholds are crossed

The system is designed to be:

- **Modular**: Each functionality is in its own file/module
- **Configurable**: Features can be enabled/disabled via a central configuration file
- **Extensible**: New modules can be added without changing existing ones
- **Self-healing**: Contains debugging tools to troubleshoot issues
- **Robust**: Includes retry logic, log rotation, and comprehensive error handling
- **Visual**: Provides dashboard components for monitoring and interaction

## Directory Structure

```
/config/python_scripts/
├── common/                 # Common utilities
│   ├── __init__.py
│   ├── config_manager.py   # Configuration management
│   ├── logger.py           # Logging functionality
│   └── notification.py     # Notification services (Telegram)
├── services/               # Service modules
│   ├── __init__.py
│   ├── grocy.py            # Grocy integration
│   ├── grocy_dashboard.py  # Grocy dashboard data provider
│   ├── weather.py          # Weather forecasting
│   ├── devices.py          # Device monitoring
│   ├── alarm_voltage_measure.py # Voltage monitoring
│   └── storage.py          # Storage management
├── debug/                  # Debugging tools
│   ├── __init__.py
│   ├── grocy_debug.py      # Grocy API testing
│   ├── telegram_debug.py   # Telegram notification testing
│   └── weather_debug.py    # Weather API testing
├── feature_flags.yaml      # Feature configuration
├── run.py                  # Main entry point
├── run_wrapper.sh          # Shell wrapper
├── diagnose.py             # System diagnostics
├── process_grocy_data.py   # Grocy data processor for dashboard
└── token_reader.py         # Token reading utility

/config/www/
├── grocy_dashboard_data.json # Raw Grocy data
├── grocy_processed/        # Processed data for dashboard
│   ├── summary.json        # Summary of all chores
│   ├── index.json          # Index of chore IDs to names
│   └── chore_*.json        # Individual chore files
├── grocy-dynamic-card.js   # Dashboard card for Grocy chores
└── logs/                   # Log files for all modules
```

Main Components
1. Core Files
/config/python_scripts/run.py
The main entry point for all automation tasks. It processes command-line arguments and calls the appropriate service module.
Purpose: Centralizes execution and handles command-line arguments
Operation:

Modes:

- grocy: Fetches chores from Grocy and sends notifications
- weather: Processes weather data and sends forecasts/alerts
- device: Monitors device status changes
- alarm_voltage: Monitors voltage levels and sends alerts
- grocy_dashboard: Updates dashboard data from Grocy
- storage: Manages log files and storage

Parses command-line arguments for module selection and parameters
Loads the appropriate module based on the --mode parameter
Handles common functionality like token validation
Sets up logging and error handling

Troubleshooting:

If run.py fails, check permissions with chmod +x /config/python_scripts/run.py
Verify Python path with diagnose.py
Check logs at /config/www/logs/main.log

/config/python_scripts/feature_flags.yaml
Configuration file that enables/disables features.
Purpose: Provides centralized control over which features are active
Operation:

Uses YAML format with sections for each module
Each module has a master switch (enabled) and feature-specific flags
Changes take effect immediately without restarting Home Assistant

Troubleshooting:

Run python3 /config/python_scripts/debug_config.py to verify configuration loading
Check for YAML syntax issues with proper indentation
Ensure the file is readable by Home Assistant user

/config/python_scripts/run_wrapper.sh
Shell script that sets up the Python environment and calls run.py.
Purpose: Ensures correct PYTHONPATH and handles log redirection
Operation:

Sets the PYTHONPATH to include the python_scripts directory
Creates and manages log files based on module being run
Captures return codes and logs execution details
Rotates log files when they get too large

2. Dashboard Components
/config/python_scripts/services/grocy_dashboard.py

Provides data for the Grocy dashboard card.
Functions:

- format_chores_for_dashboard: Formats chore data for the dashboard
- save_dashboard_data: Saves formatted data to JSON file
- update_dashboard_data: Updates the dashboard data from Grocy

/config/python_scripts/process_grocy_data.py
Processes the raw Grocy data into individual files for the dashboard card.
Process:

1. Reads /config/www/grocy_dashboard_data.json
2. Creates summary and index files
3. Splits data into individual chore files
4. Saves all files to /config/www/grocy_processed/

/config/www/grocy-dynamic-card.js
Custom Lovelace card for displaying and filtering Grocy chores.
Features:

- Displays chores with detailed information
- Filters by Territory, Location, and Person
- Color-coding for due dates
- Distinguishes between chores and tasks

Dashboard Integration
Grocy Chores Dashboard
The system includes a custom dashboard for Grocy chores with filtering capabilities.
Setup:

1. Data Flow:

- update_grocy_dashboard shell command fetches data from Grocy
- process_grocy_data processes this into smaller files
- Dashboard card reads these files and displays them


2. Adding the Card:

- Go to Dashboard > Edit Dashboard > Add Card > Manual
- ADD: 
type: custom:grocy-dynamic-card
title: Grocy Chores and Tasks

3. Automation:

- An hourly automation updates the dashboard

- id: update_process_grocy_data
  alias: Update and Process Grocy Data
  trigger:
    - platform: time_pattern
      hours: "/1"
  action:
    - service: shell_command.update_grocy_dashboard
    - delay: "00:00:02"
    - service: shell_command.process_grocy_data


**Configuration**

/config/python_scripts/feature_flags.yaml

Feature Flags
The feature_flags.yaml file controls which features are enabled:
yamlCopyweather:
  enabled: true  # Master switch for all weather features
  daily_forecast: true  # Daily temperature forecast
  extreme_weather_alert: true  # Notifications for rain, wind, snow

devices:
  enabled: true  # Master switch for all device monitoring
  shelly_caldaia_notifications: true  # Shelly relay status notifications

grocy:
  enabled: true  # Master switch for Grocy integration
  chores_notification: true  # Daily chores notifications
  dashboard_enabled: true  # Enable dashboard integration


voltage_monitoring:
  enabled: true  # Master switch for voltage monitoring
  uni_alarm: true  # Enable UNI voltage alarm specifically
  high_threshold: 9.0  # High voltage threshold (V)
  low_threshold: 3.0  # Low voltage threshold (V)

notifications:
  telegram_enabled: true  # Enable/disable all Telegram notifications
  log_to_file: true  # Log notifications to file for debugging

debug:
  verbose_logging: true  # Enable detailed logging

To disable a feature, set its value to false. The changes take effect immediately without restarting Home Assistant.
Available Modules
Weather Module
Processes weather data and sends notifications about:

Daily temperature forecasts
Extreme weather alerts (rain, wind, snow)

Troubleshooting:

Run python3 /config/python_scripts/debug/weather_debug.py [token] [entity_id] entity to test entity
Run python3 /config/python_scripts/debug/weather_debug.py [token] [entity_id] service to test forecast service
Check logs at /config/www/logs/weather.log
Verify the weather entity exists and has forecast data

Grocy Module
Integrates with Grocy to:

- Check for upcoming chores
- Send formatted notifications with details

Troubleshooting:

Run python3 /config/python_scripts/debug/grocy_debug.py [grocy_url] [grocy_api_key] connection to test API connection
Check logs at /config/www/logs/grocy.log
Verify Grocy URL and API key in Home Assistant

Devices Module
Monitors device status and sends notifications:

Shelly Caldaia relay state changes

Troubleshooting:

Check entity ID in Home Assistant
Verify device is accessible and reporting states
Check logs at /config/www/logs/devices.log

Voltage Monitoring Module
Monitors voltage levels from sensors and sends alarm notifications:

Alerts when voltage exceeds high threshold
Resets alarm when voltage drops below low threshold
Keeps track of alarm state to prevent duplicate notifications

Troubleshooting:

Run python3 /config/python_scripts/debug/voltage_debug.py [token] [entity_id] to test voltage monitoring
Check entity ID is correct and reporting voltage values
Check logs at /config/www/logs/alarm_voltage.log

Debug Tools
The system includes several diagnostic utilities:
Quick System Check
For a rapid system-wide check:
bashCopypython3 /config/python_scripts/diagnose.py
This checks file structure, permissions, and basic configuration.
Specific Module Testing
To test individual modules:
bashCopypython3 /config/python_scripts/test_automations.py [grocy|weather|devices|voltage]
This runs the module with current configuration and reports success/failure.
Automation Diagnostics
For more detailed diagnostics including token validation:
bashCopypython3 /config/python_scripts/automation_check.py test all
This performs deeper tests on all modules and identifies specific issues.
Log Management
To manage log files:
bashCopypython3 /config/python_scripts/log_manager.py
This rotates large logs, cleans up old logs, and creates a summary.
How to Run
From Home Assistant
The system is integrated with Home Assistant through shell commands and can be triggered via:

Automations
Scripts
Services

Manual Execution
You can run modules directly from the command line:
bashCopy# Run Grocy module
python3 /config/python_scripts/run.py --mode grocy --hass-token "YOUR_TOKEN" --grocy-url "YOUR_URL" --grocy-api-key "YOUR_KEY"

# Run Weather module
python3 /config/python_scripts/run.py --mode weather --hass-token "YOUR_TOKEN"

# Run Voltage monitoring
python3 /config/python_scripts/run.py --mode voltage --hass-token "YOUR_TOKEN" --voltage-entity "YOUR_VOLTAGE_ENTITY"

# Debug Grocy
python3 /config/python_scripts/debug/grocy_debug.py "YOUR_URL" "YOUR_KEY" "endpoints"
Troubleshooting Common Issues
Telegram Notifications Not Working

Test the Telegram connection:
bashCopypython3 /config/python_scripts/debug/telegram_debug.py $(cat /config/token.txt) "Test message" simple

Verify Telegram integration in Home Assistant
Check notifications.telegram_enabled is true in feature_flags.yaml

Modules Failing to Run

Check log files in /config/www/logs/
Verify file permissions:
bashCopychmod +x /config/python_scripts/*.py
chmod +x /config/python_scripts/*.sh

Run the diagnostic tool:
bashCopypython3 /config/python_scripts/diagnose.py


Invalid Entity State Errors
If you see "Invalid state with length X characters" errors:

Check your command_line sensors in configuration.yaml
Limit output length with commands like tail -n 10 or head -n 10
Use grep to extract specific information instead of full logs

Finding Entity IDs
To find entity IDs:

Go to Developer Tools > States in Home Assistant
Search for keywords (e.g., "voltage", "shelly", "weather")
Note the entity_id values for use in your automations

Extending the System
To add a new feature:

Create Module File: Add a new Python file in /config/python_scripts/services/
Update feature_flags.yaml: Add your module's configuration section
Modify run.py: Add a new mode and function to handle your module
Add Shell Commands: Update shell_command.yaml with commands to invoke your module
Add Automations: Update automations.yaml if you want automatic execution
Create Debug Tool: Add a debug script in /config/python_scripts/debug/ for testing
Update Documentation: Add details about your module to this README

**Adding Custom Cards**
When creating custom cards for the dashboard:

1. File Placement:

Save JavaScript files to /config/www/
For complex cards with multiple files, create a subdirectory


2. Registration:

Go to Settings > Dashboards > Resources
Add URL: /local/your-card-name.js
Type: JavaScript Module


3. Card Implementation:

Use class-based custom elements
Implement setConfig and set hass methods
Register with customElements.define
Add to window.customCards array


4. Data Processing:

For large datasets, split data into smaller files
Use summary and index files for efficient loading
Process data server-side with Python scripts



Troubleshooting
Dashboard Issues

- Card Not Found: Check if the JavaScript file exists and is registered as a resource
- No Data Showing: Run shell_command.update_grocy_dashboard and shell_command.process_grocy_data
- JavaScript Errors: Open browser developer tools (F12) > Console to see errors

Common Issues

- File Permissions: Ensure files are readable with chmod 644 /config/www/*.js
- YAML Syntax: Check for proper indentation in configuration files
- Missing Data: Verify that source data files exist and have content
- Resource Conflicts: Remove duplicate resource entries

Extending the System
To add a new dashboard component:

1. Create a data provider in /config/python_scripts/services/
2. Add a processor script if needed
3. Create a JavaScript card file in /config/www/
4. Register the card as a resource
5. Add automations to update the data regularly
6. Add the card to your dashboard using the Raw Configuration Editor

Best Practices

1. Start Simple: Begin with minimal functionality that works
2. Test Incrementally: Test each step before adding complexity
3. Use Static Data: Initially test with static data before connecting to real sources
4. Check File Loading: Verify resources load correctly in browser dev tools
5. Handle Large Data: Split large datasets into smaller files
6. Use Raw Configuration: Add custom cards using the Raw Configuration Editor
7. Keep Cards Isolated: Use unique names for custom elements to avoid conflicts


Maintenance
Regular Tasks

Log Management:

Run python3 /config/python_scripts/log_manager.py weekly
This is automated with a daily schedule at 4:00 AM


Configuration Backups:

Regularly back up /config/python_scripts/ directory
Include custom scripts and configuration files


Monitoring Automation Health:

Check Home Assistant automation history
Review /config/www/logs/summary.log regularly
Run python3 /config/python_scripts/automation_check.py monthly

## Voltage Alarm Monitoring

The system monitors voltage from a Shelly Plus UNI device and sends notifications when voltage crosses defined thresholds:

- When voltage rises above 9.0V, an alarm notification is sent
- When voltage falls below 3.0V after an alarm, a reset notification is sent

### Components:
- `python_scripts/services/alarm_voltage_measure.py`: Main functionality
- `python_scripts/debug/alarm_voltage_debug.py`: Debug utilities
- `input_boolean.voltage_alarm_active`: Tracks alarm state

Credits
This modular automation system was created for Home Assistant Green to provide a flexible and maintainable approach to automations.
"""
Service modules for Home Assistant automation
"""
# Import specific functions for easier access
# Change from relative imports to absolute imports
from common import get_logger, send_telegram, config_manager

# Now import and expose the service functions
from services.grocy import notify_chores
from services.weather import process_weather_data
from services.devices import monitor_device_change, notify_shelly_caldaia_status
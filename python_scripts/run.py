#!/usr/bin/env python3
"""
Main script for Home Assistant automations
Loads feature flags and runs enabled modules
"""
import sys
import argparse
import traceback
import os
import logging

# Create logs directory if it doesn't exist
os.makedirs("/config/www/logs", exist_ok=True)

# Configure basic logging first thing
logging.basicConfig(
    filename="/config/www/logs/main.log",
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Log startup information
logging.info("=== Starting automation script ===")
logging.info(f"Python version: {sys.version}")
logging.info(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")

# Ensure the current directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    logging.info(f"Added {current_dir} to sys.path")

# Now import the modules
try:
    # First import the common modules
    from common.logger import get_logger
    from common.config_manager import config_manager
    from common.notification import send_telegram
    
    # Create logger for this module
    logger = get_logger("run")
    
    # Then import the service modules
    from services.storage import manage_storage
    from services.grocy import notify_chores
    from services.weather import process_weather_data
    from services.devices import monitor_device_change, notify_shelly_caldaia_status
    from services.alarm_voltage_measure import check_voltage_alarm
    from services.grocy_dashboard import update_dashboard_data
    
    logger.info("Successfully imported all modules")
except ImportError as e:
    logging.error(f"Import error: {str(e)}")
    logging.error(f"Traceback: {traceback.format_exc()}")
    raise

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run Home Assistant automations")
    
    # Add the mode argument
    parser.add_argument("--mode", choices=["grocy", "weather", "device", "alarm_voltage", "grocy_dashboard", "storage", "all"],
                        help="Automation mode to run", required=True)
    
    # Common arguments
    parser.add_argument("--hass-token", help="Home Assistant token", required=True)
    parser.add_argument("--hass-url", help="Home Assistant URL", default="http://localhost:8123")
    
    # Grocy-specific arguments
    parser.add_argument("--grocy-url", help="Grocy API URL")
    parser.add_argument("--grocy-api-key", help="Grocy API key")
    
    # Weather-specific arguments
    parser.add_argument("--weather-entity", help="Weather entity ID", default="weather.openweathermap")
    
    # Device-specific arguments
    parser.add_argument("--device-entity", help="Device entity ID")
    parser.add_argument("--device-state", help="Device state (on/off)")

    # Voltage-specific arguments
    parser.add_argument("--voltage-entity", help="Voltage sensor entity ID")
    parser.add_argument("--previous-state-entity", help="Entity ID that tracks previous alarm state")
    parser.add_argument("--voltage-state-entity", help="Entity ID that tracks voltage alarm state")

    # Storage-specific arguments
    parser.add_argument("--max-log-size", type=int, help="Maximum log file size in KB", default=1024)
    parser.add_argument("--max-log-age", type=int, help="Maximum log file age in days", default=30) 

    return parser.parse_args()

def run_grocy(args):
    """Run the Grocy module"""
    if not config_manager.is_enabled('grocy.enabled'):
        logger.info("Grocy integration is disabled in configuration")
        return False
    
    if not args.grocy_url or not args.grocy_api_key:
        logger.error("Grocy URL and API key are required for Grocy mode")
        return False
    
    logger.section("Running Grocy Module")
    return notify_chores(args.grocy_url, args.grocy_api_key, args.hass_token, args.hass_url)

def run_grocy_dashboard(args):
    """Run the Grocy dashboard data provider"""
    logger.section("Running Grocy Dashboard Provider")
    
    # Debug: Log all arguments
    logger.info(f"Received arguments: {vars(args)}")
    
    # Check feature flag with detailed logging
    dashboard_enabled = config_manager.is_enabled('grocy.dashboard_enabled')
    logger.info(f"grocy.dashboard_enabled flag: {dashboard_enabled}")
    
    if not dashboard_enabled:
        logger.info("Grocy dashboard is disabled in configuration")
        return False
    
    # Check required arguments with detailed logging
    has_grocy_url = bool(args.grocy_url)
    has_grocy_api_key = bool(args.grocy_api_key)
    
    logger.info(f"Has grocy_url: {has_grocy_url}, Has grocy_api_key: {has_grocy_api_key}")
    
    if not has_grocy_url or not has_grocy_api_key:
        logger.error("Grocy URL and API key are required for Grocy dashboard")
        return False
    
    try:
        # Import with explicit error handling
        logger.info("Attempting to import update_dashboard_data function")
        from services.grocy_dashboard import update_dashboard_data
        logger.info("Successfully imported update_dashboard_data function")
        
        # Call the function with explicit error handling
        logger.info(f"Calling update_dashboard_data with URL: {args.grocy_url[:10]}... and API key: {args.grocy_api_key[:5]}...")
        result = update_dashboard_data(args.grocy_url, args.grocy_api_key)
        logger.info(f"update_dashboard_data returned: {result}")
        
        return result
    except Exception as e:
        logger.error(f"Error in run_grocy_dashboard: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def run_weather(args):
    """Run the Weather module"""
    if not config_manager.is_enabled('weather.enabled'):
        logger.info("Weather features are disabled in configuration")
        return False
    
    logger.section("Running Weather Module")
    return process_weather_data(args.hass_url, args.hass_token, args.weather_entity)

def run_device(args):
    """Run the Device monitoring module"""
    if not config_manager.is_enabled('devices.enabled'):
        logger.info("Device monitoring is disabled in configuration")
        return False
    
    if not args.device_entity:
        logger.error("Device entity ID is required for device mode")
        return False
    
    logger.section("Running Device Module")
    return notify_shelly_caldaia_status(args.hass_url, args.hass_token, args.device_entity, args.device_state)

def run_voltage(args):
    """Run the Voltage monitoring module"""
    if not config_manager.is_enabled('voltage_monitoring.enabled'):
        logger.info("Voltage monitoring is disabled in configuration")
        return False
    
    if not args.voltage_entity:
        logger.error("Voltage entity ID is required for voltage mode")
        return False
    
    logger.section("Running Voltage Monitoring Module")
    
    # Handle previous state entity if provided
    previous_state_entity = args.previous_state_entity if hasattr(args, 'previous_state_entity') else None
    
    return check_voltage_alarm(args.hass_url, args.hass_token, args.voltage_entity, previous_state_entity)

def run_alarm_voltage(args):
    """Run the Alarm Voltage measurement module"""
    if not config_manager.is_enabled('voltage_monitoring.enabled'):
        logger.info("Voltage monitoring is disabled in configuration")
        return False
    
    if not args.voltage_entity:
        logger.error("Voltage entity ID is required for alarm voltage mode")
        return False
    
    logger.section("Running Alarm Voltage Module")
    
    # Import here to avoid circular imports
    from services.alarm_voltage_measure import check_voltage_alarm
    
    state_entity = args.voltage_state_entity if hasattr(args, 'voltage_state_entity') else None
    
    return check_voltage_alarm(args.hass_url, args.hass_token, args.voltage_entity, state_entity)

def run_storage(args):
    """Run the Storage management module"""
    if not config_manager.is_enabled('storage.enabled'):
        logger.info("Storage management is disabled in configuration")
        return False
    
    logger.section("Running Storage Management Module")
    return manage_storage(args.hass_url, args.hass_token, args.max_log_size, args.max_log_age)


def main():
    """Main function to run the selected automation"""
    try:
        # Parse arguments
        args = parse_arguments()
        logger.info(f"Running in {args.mode} mode")
        
        # Run the selected mode
        if args.mode == "grocy":
            success = run_grocy(args)
        elif args.mode == "weather":
            success = run_weather(args)
        elif args.mode == "device":
            success = run_device(args)
        elif args.mode == "all":
            # Run all enabled modules
            grocy_success = run_grocy(args) if config_manager.is_enabled('grocy.enabled') else True
            weather_success = run_weather(args) if config_manager.is_enabled('weather.enabled') else True
            device_success = run_device(args) if config_manager.is_enabled('devices.enabled') else True
            success = grocy_success and weather_success and device_success
        elif args.mode == "voltage":
            success = run_voltage(args)
        elif args.mode == "alarm_voltage":
            success = run_alarm_voltage(args)
        elif args.mode == "grocy_dashboard":
            success = run_grocy_dashboard(args)
        elif args.mode == "storage":
            success = run_storage(args)
        else:
            logger.error(f"Unknown mode: {args.mode}")
            success = False
        
        if success:
            logger.info(f"Successfully completed {args.mode} automation")
        else:
            logger.error(f"Failed to complete {args.mode} automation")
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Error running automation: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
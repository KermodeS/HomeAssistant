#!/usr/bin/env python3
"""
Debug utility for voltage monitoring in Home Assistant
"""
import sys
import os
import requests
import datetime

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from common.logger import get_logger
    from services.alarm_voltage_measure import get_uni_voltage, check_voltage_alarm
except ImportError as e:
    # Fallback logger
    class SimpleLogger:
        def __init__(self, name):
            self.name = name
            print(f"Created simple logger for {name}")
        
        def section(self, title):
            divider = "=" * len(title)
            print(f"\n{divider}\n{title}\n{divider}")
        
        def info(self, message):
            print(f"[INFO] {message}")
        
        def error(self, message):
            print(f"[ERROR] {message}")
        
        def debug(self, message):
            print(f"[DEBUG] {message}")
    
    get_logger = lambda name: SimpleLogger(name)
    
    def get_uni_voltage(hass_url, hass_token, entity_id):
        print(f"[ERROR] Could not import get_uni_voltage function")
        return None
    
    def check_voltage_alarm(hass_url, hass_token, entity_id, previous_state_entity_id=None):
        print(f"[ERROR] Could not import check_voltage_alarm function")
        return False

# Set up logger
logger = get_logger("voltage_debug")


def test_voltage_entity(hass_url, hass_token, entity_id):
    """
    Test if a voltage entity exists and get its value
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Voltage entity ID
    """
    logger.section(f"Testing Voltage Entity: {entity_id}")
    
    try:
        url = f"{hass_url}/api/states/{entity_id}"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Checking entity state at: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Entity exists")
            
            # Parse the state data
            state_data = response.json()
            state = state_data.get("state", "unknown")
            logger.info(f"Current state: {state}")
            
            # Try to convert to float
            try:
                voltage = float(state)
                logger.info(f"Current voltage: {voltage}V")
            except (ValueError, TypeError):
                logger.error(f"❌ Could not convert state '{state}' to a voltage value")
            
            # Check attributes
            attributes = state_data.get("attributes", {})
            logger.info(f"Attributes: {', '.join(attributes.keys())}")
            
        else:
            logger.error(f"❌ Failed to get entity state: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error testing voltage entity: {str(e)}")


def test_voltage_thresholds(hass_url, hass_token, entity_id):
    """
    Test voltage alarm thresholds
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Voltage entity ID
    """
    logger.section("Testing Voltage Thresholds")
    
    try:
        # Get current voltage
        current_voltage = get_uni_voltage(hass_url, hass_token, entity_id)
        
        if current_voltage is not None:
            logger.info(f"Current voltage: {current_voltage}V")
            
            # Check against different thresholds
            thresholds = [
                (current_voltage - 2, current_voltage - 1),  # Below current
                (current_voltage + 1, current_voltage + 2),  # Above current
                (3.0, 9.0)  # Default thresholds
            ]
            
            for i, (low, high) in enumerate(thresholds):
                logger.info(f"Test {i+1}: Low={low}V, High={high}V")
                
                if current_voltage <= low:
                    logger.info(f"Current voltage {current_voltage}V is <= low threshold {low}V")
                elif current_voltage >= high:
                    logger.info(f"Current voltage {current_voltage}V is >= high threshold {high}V")
                else:
                    logger.info(f"Current voltage {current_voltage}V is between thresholds")
        else:
            logger.error("❌ Failed to get current voltage")
            
    except Exception as e:
        logger.error(f"Error testing voltage thresholds: {str(e)}")


def main():
    """Main function to run tests based on command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: voltage_debug.py <hass_token> [entity_id] [test_type]")
        print("  test_type: entity, thresholds, alarm (default: all)")
        return
    
    hass_token = sys.argv[1]
    hass_url = "http://localhost:8123"
    
    # Use custom entity_id if provided
    entity_id = "sensor.shelly_uni_voltage"
    if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        entity_id = sys.argv[2]
        
    # Determine which test to run
    test_type = "all"
    if len(sys.argv) > 3:
        test_type = sys.argv[3].lower()
        
    logger.section("Voltage Monitoring Debug")
    
    if test_type == "entity" or test_type == "all":
        test_voltage_entity(hass_url, hass_token, entity_id)
        
    if test_type == "thresholds" or test_type == "all":
        test_voltage_thresholds(hass_url, hass_token, entity_id)
        
    if test_type == "alarm" or test_type == "all":
        # Use a temporary input_boolean for testing
        temp_input_boolean = "input_boolean.voltage_debug_test"
        logger.section("Testing Voltage Alarm")
        result = check_voltage_alarm(hass_url, hass_token, entity_id, temp_input_boolean)
        logger.info(f"Alarm check result: {'✅ Success' if result else '❌ Failed'}")
        
    logger.section("Debug Complete")


if __name__ == "__main__":
    main()
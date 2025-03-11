#!/usr/bin/env python3
"""
Debug utility for alarm voltage monitoring in Home Assistant
Tests Shelly UNI voltage sensor and alarm thresholds
"""
import requests
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from common.logger import get_logger
except ImportError:
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

# Set up logger
logger = get_logger("alarm_voltage_debug")


def test_voltage_sensor(hass_url, hass_token, entity_id):
    """
    Test reading voltage from a sensor entity
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the voltage sensor
    """
    logger.section(f"Testing Voltage Sensor: {entity_id}")
    
    try:
        url = f"{hass_url}/api/states/{entity_id}"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Checking sensor state at: {url}")
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
                
                # Check if this looks like a valid voltage reading
                if 0 <= voltage <= 15:  # Reasonable range for Shelly UNI ADC
                    logger.info("✅ Voltage reading appears valid")
                else:
                    logger.info("⚠️ Voltage reading outside expected range (0-15V)")
                
            except (ValueError, TypeError):
                logger.error(f"❌ Could not convert state '{state}' to float")
                
            # Check attributes
            attributes = state_data.get("attributes", {})
            logger.info(f"Attributes: {', '.join(attributes.keys())}")
            
            # Check for unit_of_measurement
            unit = attributes.get("unit_of_measurement")
            if unit:
                logger.info(f"Unit: {unit}")
                if unit.lower() in ["v", "volt", "volts", "vdc"]:
                    logger.info("✅ Unit appears to be voltage")
                else:
                    logger.error(f"❌ Unit '{unit}' does not appear to be voltage")
            else:
                logger.warning("⚠️ No unit_of_measurement attribute found")
                
        else:
            logger.error(f"❌ Failed to get entity state: {response.status_code}")
            logger.debug(f"Response: {response.text}")
            
    except Exception as e:
        logger.error(f"Error testing voltage sensor: {str(e)}")


def simulate_alarm_logic(hass_url, hass_token, entity_id, high_threshold=9.0, low_threshold=3.0):
    """
    Simulate the alarm logic with current voltage reading
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the voltage sensor
        high_threshold: High voltage threshold
        low_threshold: Low voltage threshold
    """
    logger.section("Simulating Alarm Logic")
    
    try:
        # Get current voltage
        url = f"{hass_url}/api/states/{entity_id}"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            state_data = response.json()
            state = state_data.get("state", "unknown")
            
            try:
                current_voltage = float(state)
                logger.info(f"Current voltage: {current_voltage}V")
                
                # Simulate alarm logic
                logger.info(f"Using thresholds: High={high_threshold}V, Low={low_threshold}V")
                
                # Check both scenarios
                logger.info("Scenario 1: If previous state was NOT alarmed:")
                if current_voltage >= high_threshold:
                    logger.info("✅ Would TRIGGER alarm (voltage >= high threshold)")
                else:
                    logger.info("❌ Would NOT trigger alarm (voltage < high threshold)")
                
                logger.info("Scenario 2: If previous state WAS alarmed:")
                if current_voltage <= low_threshold:
                    logger.info("✅ Would RESET alarm (voltage <= low threshold)")
                else:
                    logger.info("❌ Would NOT reset alarm (voltage > low threshold)")
                
            except (ValueError, TypeError):
                logger.error(f"❌ Could not convert state '{state}' to float")
        else:
            logger.error(f"❌ Failed to get entity state: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error simulating alarm logic: {str(e)}")


def main():
    """Main function to run tests based on command line arguments"""
    if len(sys.argv) < 3:
        print("Usage: alarm_voltage_debug.py <hass_token> <entity_id> [high_threshold] [low_threshold]")
        return
    
    hass_token = sys.argv[1]
    entity_id = sys.argv[2]
    hass_url = "http://localhost:8123"
    
    # Get optional thresholds
    high_threshold = 9.0
    low_threshold = 3.0
    
    if len(sys.argv) > 3:
        try:
            high_threshold = float(sys.argv[3])
        except ValueError:
            logger.error(f"Invalid high threshold: {sys.argv[3]}")
    
    if len(sys.argv) > 4:
        try:
            low_threshold = float(sys.argv[4])
        except ValueError:
            logger.error(f"Invalid low threshold: {sys.argv[4]}")
    
    logger.section("Voltage Alarm Debug")
    
    # Test voltage sensor
    test_voltage_sensor(hass_url, hass_token, entity_id)
    
    # Simulate alarm logic
    simulate_alarm_logic(hass_url, hass_token, entity_id, high_threshold, low_threshold)
    
    logger.section("Debug Complete")


if __name__ == "__main__":
    main()
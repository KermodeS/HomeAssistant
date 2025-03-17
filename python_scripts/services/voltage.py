#!/usr/bin/env python3
"""
Voltage monitoring service for Home Assistant
Monitors voltage levels and sends notifications when thresholds are exceeded
"""
import requests
import sys
from common import get_logger, send_telegram, config_manager

# Set up logger
logger = get_logger("alarm_voltage")

def get_voltage(hass_url, hass_token, entity_id):
    """
    Get the current voltage reading from the specified entity
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the voltage sensor
        
    Returns:
        float: Current voltage or None on failure
    """
    try:
        url = f"{hass_url}/api/states/{entity_id}"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        logger.debug(f"Fetching voltage for {entity_id}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            state_data = response.json()
            state = state_data.get("state")
            
            try:
                voltage = float(state)
                logger.info(f"Current voltage for {entity_id}: {voltage:.2f}V")
                return voltage
            except (ValueError, TypeError):
                logger.error(f"Failed to convert voltage value '{state}' to float")
                return None
        else:
            logger.error(f"Error fetching voltage: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Exception getting voltage: {str(e)}")
        return None

def get_alarm_state(hass_url, hass_token, state_entity_id):
    """
    Get the current alarm state from the specified entity
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        state_entity_id: Entity ID that tracks the alarm state
        
    Returns:
        bool: Current alarm state (True if active, False if inactive) or None on failure
    """
    try:
        url = f"{hass_url}/api/states/{state_entity_id}"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            state_data = response.json()
            state = state_data.get("state", "off").lower()
            
            is_active = state == "on" or state == "true"
            return is_active
        else:
            logger.error(f"Error fetching alarm state: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Exception getting alarm state: {str(e)}")
        return None

def set_alarm_state(hass_url, hass_token, state_entity_id, active):
    """
    Set the alarm state
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        state_entity_id: Entity ID that tracks the alarm state
        active: True to set alarm active, False to deactivate
        
    Returns:
        bool: Success status
    """
    try:
        logger.debug(f"Setting alarm state to {active}")
        
        service = "input_boolean.turn_on" if active else "input_boolean.turn_off"
        url = f"{hass_url}/api/services/{service}"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "entity_id": state_entity_id
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Successfully updated alarm state to {active}")
            return True
        else:
            logger.error(f"Error updating alarm state: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Exception setting alarm state: {str(e)}")
        return False

def check_voltage_alarm(hass_url, hass_token, entity_id, state_entity_id=None, high_threshold=None, low_threshold=None):
    """
    Check voltage level and trigger alarm if thresholds are exceeded
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the voltage sensor
        state_entity_id: Entity ID that tracks the alarm state
        high_threshold: High voltage threshold (default from config)
        low_threshold: Low voltage threshold (default from config)
        
    Returns:
        bool: True if alarm was triggered or reset, False otherwise
    """
    logger.section("Checking Voltage Alarm")
    
    if not config_manager.is_enabled('voltage_monitoring.enabled'):
        logger.info("Voltage monitoring is disabled in configuration")
        return False
    
    # Use default thresholds from config if not provided
    if high_threshold is None:
        high_threshold = config_manager.get_config_value('voltage_monitoring.high_threshold', 9.0)
    if low_threshold is None:
        low_threshold = config_manager.get_config_value('voltage_monitoring.low_threshold', 3.0)
    
    # Use default state entity if not provided
    if state_entity_id is None:
        state_entity_id = config_manager.get_config_value(
            'voltage_monitoring.state_entity', 
            'input_boolean.voltage_alarm_active'
        )
    
    logger.info(f"Using thresholds: high={high_threshold}V, low={low_threshold}V")
    
    # Get current voltage
    voltage = get_voltage(hass_url, hass_token, entity_id)
    if voltage is None:
        logger.error(f"Failed to get voltage for {entity_id}")
        return False
    
    # Get current alarm state
    previously_alarmed = get_alarm_state(hass_url, hass_token, state_entity_id)
    if previously_alarmed is None:
        logger.error(f"Failed to get alarm state from {state_entity_id}")
        return False
    
    logger.info(f"Previous alarm state: {previously_alarmed}")
    
    # Check voltage levels
    logger.info(f"Current voltage: {voltage:.2f}V, High threshold: {high_threshold}V, Low threshold: {low_threshold}V")
    
    # Alarm logic - trigger an alarm if:
    # 1. Voltage is above high threshold and alarm was not previously triggered
    # 2. Voltage is below low threshold and alarm was not previously triggered
    # Reset alarm if:
    # Voltage is back within thresholds and alarm was previously triggered
    
    alarm_triggered = False
    message = ""
    title = ""
    
    if voltage > high_threshold and not previously_alarmed:
        logger.info(f"ALARM: Voltage ({voltage:.2f}V) is above threshold ({high_threshold}V)")
        logger.info("✅ ALARM CONDITION MET: Voltage above threshold and not previously alarmed")
        alarm_triggered = True
        
        title = "Voltage Alarm Triggered"
        message = (
            f"🚨 ALARM: Voltage level is too high!\n"
            f"Current: {voltage:.2f}V\n"
            f"Threshold: {high_threshold}V\n"
            f"Entity: {entity_id}"
        )
    elif voltage < low_threshold and not previously_alarmed:
        logger.info(f"ALARM: Voltage ({voltage:.2f}V) is below threshold ({low_threshold}V)")
        logger.info("✅ ALARM CONDITION MET: Voltage below threshold and not previously alarmed")
        alarm_triggered = True
        
        title = "Voltage Alarm Triggered"
        message = (
            f"🚨 ALARM: Voltage level is too low!\n"
            f"Current: {voltage:.2f}V\n"
            f"Threshold: {low_threshold}V\n"
            f"Entity: {entity_id}"
        )
    elif previously_alarmed and low_threshold <= voltage <= high_threshold:
        logger.info(f"RESET: Voltage ({voltage:.2f}V) is back within normal range")
        logger.info("✅ RESET CONDITION MET: Voltage within normal range and previously alarmed")
        
        title = "Voltage Alarm Reset"
        message = (
            f"✅ RESET: Voltage level is back to normal.\n"
            f"Current: {voltage:.2f}V\n"
            f"Thresholds: {low_threshold}V - {high_threshold}V\n"
            f"Entity: {entity_id}"
        )
        
        # Reset alarm state
        if set_alarm_state(hass_url, hass_token, state_entity_id, False):
            return True
        else:
            logger.error("Failed to reset alarm state")
            return False
    
    # Send notification if alarm triggered
    if alarm_triggered and message:
        send_telegram(message, hass_token, title=title)
        
        # Update alarm state
        if set_alarm_state(hass_url, hass_token, state_entity_id, True):
            return True
        else:
            logger.error("Failed to set alarm state")
            return False
    
    return False

def reset_voltage_alarm(hass_url, hass_token, entity_id, state_entity_id=None, threshold=None):
    """
    Check if voltage is below threshold and reset alarm if it is
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the voltage sensor
        state_entity_id: Entity ID that tracks the alarm state
        threshold: Low voltage threshold (default from config)
        
    Returns:
        bool: True if alarm was reset, False otherwise
    """
    logger.section("Testing Alarm Reset")
    
    # Use default state entity if not provided
    if state_entity_id is None:
        state_entity_id = config_manager.get_config_value(
            'voltage_monitoring.state_entity', 
            'input_boolean.voltage_alarm_active'
        )
    
    # Use default threshold from config if not provided
    if threshold is None:
        threshold = config_manager.get_config_value('voltage_monitoring.low_threshold', 3.0)
    
    # Get current alarm state
    previously_alarmed = get_alarm_state(hass_url, hass_token, state_entity_id)
    if previously_alarmed is None:
        logger.error(f"Failed to get alarm state from {state_entity_id}")
        return False
    
    logger.info(f"Previous alarm state: {previously_alarmed}")
    
    # For testing, if not previously alarmed, set it to alarmed first
    if not previously_alarmed:
        logger.warning("Alarm is not currently active. Activating it for test...")
        if set_alarm_state(hass_url, hass_token, state_entity_id, True):
            logger.info("Alarm state activated for test")
        else:
            logger.error("Failed to set alarm state for test")
            return False
    
    # Simulate voltage below threshold
    test_voltage = 2.5  # Below threshold
    logger.info(f"Simulating low voltage: {test_voltage}V (below threshold)")
    
    logger.info(f"Current voltage: {test_voltage}V, Low threshold: {threshold}V")
    
    if test_voltage < threshold:
        logger.info(f"RESET: Voltage ({test_voltage}V) is below reset threshold ({threshold}V)")
        logger.info("✅ RESET CONDITION MET: Voltage below threshold and previously alarmed")
        
        title = "Voltage Alarm Reset"
        message = (
            f"✅ RESET: Voltage level is below threshold.\n"
            f"Current: {test_voltage}V\n"
            f"Threshold: {threshold}V\n"
            f"Entity: {entity_id}"
        )
        
        # Send notification
        if send_telegram(message, hass_token, title=title):
            logger.info("Reset notification sent successfully")
        else:
            logger.error("Failed to send reset notification")
            return False
        
        # Reset alarm state
        if set_alarm_state(hass_url, hass_token, state_entity_id, False):
            logger.info("Alarm state reset to False")
            logger.info("✅ Alarm reset test completed successfully")
            return True
        else:
            logger.error("Failed to reset alarm state")
            return False
    else:
        logger.info(f"Voltage ({test_voltage}V) is not below threshold ({threshold}V)")
        logger.info("❌ Reset condition not met")
        return False

def test_voltage_alarm(hass_url, hass_token, entity_id, state_entity_id=None):
    """
    Test the voltage alarm functionality
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the voltage sensor
        state_entity_id: Entity ID that tracks the alarm state
        
    Returns:
        bool: Success status
    """
    logger.info(f"Testing alarm voltage with entity: {entity_id}")
    
    # Use default state entity if not provided
    if state_entity_id is None:
        state_entity_id = config_manager.get_config_value(
            'voltage_monitoring.state_entity', 
            'input_boolean.voltage_alarm_active'
        )
    
    logger.info(f"State entity: {state_entity_id}")
    
    # Call the normal check function
    result = check_voltage_alarm(hass_url, hass_token, entity_id, state_entity_id)
    
    if result:
        logger.info("✅ Alarm voltage check completed successfully")
    else:
        logger.info("❌ No alarm conditions met during test")
    
    return result

def main():
    """Main function when run as a script"""
    # Get command line arguments
    if len(sys.argv) < 3:
        error_msg = "⚠️ Not enough arguments. Usage: voltage.py <mode> <hass_token> <voltage_entity> [state_entity]"
        logger.error(error_msg)
        print(error_msg)
        return 1
    
    mode = sys.argv[1]
    hass_token = sys.argv[2]
    entity_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    hass_url = "http://localhost:8123"
    
    # Use custom state entity if provided
    state_entity_id = None
    if len(sys.argv) > 4:
        state_entity_id = sys.argv[4]
    
    if mode == "check":
        # Regular check mode
        if entity_id:
            return 0 if check_voltage_alarm(hass_url, hass_token, entity_id, state_entity_id) else 1
        else:
            logger.error("Entity ID is required for check mode")
            return 1
    elif mode == "test":
        # Test mode
        if entity_id:
            return 0 if test_voltage_alarm(hass_url, hass_token, entity_id, state_entity_id) else 1
        else:
            logger.error("Entity ID is required for test mode")
            return 1
    elif mode == "reset":
        # Reset test mode
        if entity_id:
            return 0 if reset_voltage_alarm(hass_url, hass_token, entity_id, state_entity_id) else 1
        else:
            logger.error("Entity ID is required for reset mode")
            return 1
    else:
        logger.error(f"Unknown mode: {mode}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Alarm voltage measurement service for Home Assistant
Monitors voltage from Shelly UNI device and sends alarm notifications
"""
import requests
import sys
from common import get_logger, send_telegram, config_manager

# Set up logger
logger = get_logger("alarm_voltage")


def get_uni_voltage(hass_url, hass_token, entity_id):
    """
    Get the current voltage from a Shelly UNI entity
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the Shelly UNI sensor
        
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
            
            # Get the state value - this should be the voltage
            state = state_data.get("state")
            
            try:
                voltage = float(state)
                logger.info(f"Current voltage for {entity_id}: {voltage}V")
                return voltage
            except (ValueError, TypeError):
                logger.error(f"Could not convert voltage value '{state}' to float")
                return None
        else:
            logger.error(f"Error fetching entity state: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Exception getting voltage: {str(e)}")
        return None


def check_voltage_alarm(hass_url, hass_token, entity_id, previous_state_entity_id=None):
    """
    Monitor voltage and trigger alarm notifications based on thresholds
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the Shelly UNI voltage sensor
        previous_state_entity_id: Entity ID that tracks the previous alarm state (optional)
        
    Returns:
        bool: Success status
    """
    if not config_manager.is_enabled('voltage_monitoring.enabled'):
        logger.info("Voltage monitoring is disabled in configuration")
        return False
    
    if not config_manager.is_enabled('voltage_monitoring.uni_alarm'):
        logger.info("UNI voltage alarm is disabled in configuration")
        return False
    
    logger.section("Checking Voltage Alarm")
    
    try:
        # Get the high and low voltage thresholds from config
        high_threshold = config_manager.get_config_value('voltage_monitoring.high_threshold', 9.0)
        low_threshold = config_manager.get_config_value('voltage_monitoring.low_threshold', 3.0)
        
        logger.info(f"Using thresholds: high={high_threshold}V, low={low_threshold}V")
        
        # Get current voltage
        current_voltage = get_uni_voltage(hass_url, hass_token, entity_id)
        
        if current_voltage is None:
            logger.error(f"Failed to get voltage from {entity_id}")
            return False
        
        # Get previous alarm state if available
        previous_alarm_state = False
        if previous_state_entity_id:
            previous_alarm_state = get_previous_alarm_state(hass_url, hass_token, previous_state_entity_id)
            logger.info(f"Previous alarm state: {previous_alarm_state}")
        
        # Check voltage against thresholds
        if current_voltage >= high_threshold and not previous_alarm_state:
            # Voltage is above high threshold and alarm wasn't already triggered
            logger.info(f"ALARM: Voltage ({current_voltage}V) is above threshold ({high_threshold}V)")
            
            # Send alarm notification
            message = f"🚨 ALARM: Voltage level is {current_voltage}V, which is above the threshold of {high_threshold}V"
            send_telegram(message, hass_token, title="Voltage Alarm Triggered")
            
            # Update previous state if we have an entity for it
            if previous_state_entity_id:
                set_alarm_state(hass_url, hass_token, previous_state_entity_id, True)
                
            return True
            
        elif current_voltage <= low_threshold and previous_alarm_state:
            # Voltage dropped below low threshold and alarm was previously triggered
            logger.info(f"RESET: Voltage ({current_voltage}V) is below reset threshold ({low_threshold}V)")
            
            # Send reset notification
            message = f"✅ RESET: Voltage level is {current_voltage}V, which is below the reset threshold of {low_threshold}V"
            send_telegram(message, hass_token, title="Voltage Alarm Reset")
            
            # Update previous state if we have an entity for it
            if previous_state_entity_id:
                set_alarm_state(hass_url, hass_token, previous_state_entity_id, False)
                
            return True
        else:
            # No state change needed
            logger.info(f"No alarm condition: Current voltage is {current_voltage}V")
            return True
            
    except Exception as e:
        logger.error(f"Error checking voltage alarm: {str(e)}")
        return False


def get_previous_alarm_state(hass_url, hass_token, entity_id):
    """
    Get the previous alarm state from an input_boolean entity
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the input_boolean that stores alarm state
        
    Returns:
        bool: Previous alarm state (True if alarmed, False otherwise)
    """
    try:
        url = f"{hass_url}/api/states/{entity_id}"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            state_data = response.json()
            state = state_data.get("state", "off")
            
            # Convert state to boolean
            return state.lower() == "on"
        else:
            logger.error(f"Error fetching previous state: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Exception getting previous state: {str(e)}")
        return False


def set_alarm_state(hass_url, hass_token, entity_id, is_alarmed):
    """
    Update the alarm state in an input_boolean entity
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the input_boolean that stores alarm state
        is_alarmed: Boolean indicating whether alarm is active
        
    Returns:
        bool: Success status
    """
    try:
        # Determine the service to call
        service = "turn_on" if is_alarmed else "turn_off"
        
        url = f"{hass_url}/api/services/input_boolean/{service}"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "entity_id": entity_id
        }
        
        logger.debug(f"Setting alarm state to {is_alarmed}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"Successfully updated alarm state to {is_alarmed}")
            return True
        else:
            logger.error(f"Error updating alarm state: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Exception updating alarm state: {str(e)}")
        return False


def main():
    """Main function when run as a script"""
    # Get command line arguments
    if len(sys.argv) < 3:
        error_msg = "⚠️ Not enough arguments. Usage: alarm_voltage_measure.py <hass_token> <entity_id> [previous_state_entity]"
        logger.error(error_msg)
        print(error_msg)
        return
    
    hass_token = sys.argv[1]
    entity_id = sys.argv[2]
    hass_url = "http://localhost:8123"
    
    # Get optional previous state entity
    previous_state_entity = None
    if len(sys.argv) > 3:
        previous_state_entity = sys.argv[3]
    
    # Run voltage check
    check_voltage_alarm(hass_url, hass_token, entity_id, previous_state_entity)


if __name__ == "__main__":
    main()
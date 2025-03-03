#!/usr/bin/env python3
"""
Devices monitoring service for Home Assistant
Currently handles Shelly relay status notifications
"""
import requests
import sys
from common import get_logger, send_telegram, config_manager

# Set up logger
logger = get_logger("devices")


def get_device_state(hass_url, hass_token, entity_id):
    """
    Get the current state of a device from Home Assistant
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the device
        
    Returns:
        str: Current state or None on failure
    """
    try:
        url = f"{hass_url}/api/states/{entity_id}"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        logger.debug(f"Fetching state for {entity_id}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            state_data = response.json()
            state = state_data.get("state")
            logger.info(f"Device {entity_id} is {state}")
            return state
        else:
            logger.error(f"Error fetching device state: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Exception getting device state: {str(e)}")
        return None


def notify_shelly_caldaia_status(hass_url, hass_token, entity_id, state=None):
    """
    Send notification about Shelly Caldaia relay status
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the Shelly device
        state: Current state if already known, otherwise will be fetched
        
    Returns:
        bool: Success status
    """
    if not config_manager.is_enabled('devices.shelly_caldaia_notifications'):
        logger.info("Shelly Caldaia notifications are disabled in configuration")
        return False
    
    logger.section("Shelly Caldaia Status Notification")
    
    try:
        # Get the state if not provided
        if state is None:
            state = get_device_state(hass_url, hass_token, entity_id)
            
        if state is None:
            logger.error(f"Unable to determine state for {entity_id}")
            return False
        
        # Format message based on state
        title = "Caldaia Update"
        if state == "on":
            message = "Caldaia Shelly Relay - Now ON"
        else:
            message = "Caldaia Shelly Relay - Now OFF"
        
        # Send notification
        success = send_telegram(message, hass_token, title=title)
        
        if success:
            logger.info(f"Sent Shelly Caldaia status notification: {message}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error notifying Shelly Caldaia status: {str(e)}")
        return False


def monitor_device_change(hass_url, hass_token, entity_id, event_data=None):
    """
    Process a device state change event from Home Assistant
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Entity ID of the device
        event_data: Event data if called from an event, otherwise None
        
    Returns:
        bool: Success status
    """
    if not config_manager.is_enabled('devices.enabled'):
        logger.info("Device monitoring is disabled in configuration")
        return False
    
    # Handle Shelly Caldaia specifically
    if "shelly" in entity_id and "caldaia" in entity_id:
        # Get state from event data if available
        state = None
        if event_data and "new_state" in event_data:
            state = event_data["new_state"].get("state")
            
        return notify_shelly_caldaia_status(hass_url, hass_token, entity_id, state)
    
    # Handle other devices as needed in the future
    logger.warning(f"No specific handler for device {entity_id}")
    return False


def main():
    """Main function when run as a script"""
    # Get command line arguments
    if len(sys.argv) < 3:
        error_msg = "⚠️ Not enough arguments. Usage: devices.py <hass_token> <entity_id> [state]"
        logger.error(error_msg)
        print(error_msg)
        return
    
    hass_token = sys.argv[1]
    entity_id = sys.argv[2]
    hass_url = "http://localhost:8123"
    
    # Use provided state if available
    state = None
    if len(sys.argv) > 3:
        state = sys.argv[3]
    
    # Monitor the device
    if "shelly" in entity_id and "caldaia" in entity_id:
        notify_shelly_caldaia_status(hass_url, hass_token, entity_id, state)
    else:
        monitor_device_change(hass_url, hass_token, entity_id)


if __name__ == "__main__":
    main()
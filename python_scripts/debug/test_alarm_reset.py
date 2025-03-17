#!/usr/bin/env python3
"""
Test alarm voltage reset with simulated low voltage
"""
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from common import get_logger, send_telegram
from services.alarm_voltage_measure import get_previous_alarm_state, set_alarm_state

# Set up logger
logger = get_logger("test_alarm_reset")

# Simulate low voltage - overriding the normal function
def get_uni_voltage(hass_url, hass_token, entity_id):
    """Simulated function that returns a low voltage"""
    simulated_voltage = 2.5  # Below the 3.0V threshold
    logger.info(f"Simulating low voltage: {simulated_voltage}V (below threshold)")
    return simulated_voltage

def test_alarm_reset(hass_url, hass_token, state_entity_id, low_threshold=3.0):
    """
    Test alarm reset with simulated low voltage
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        state_entity_id: Entity ID for alarm state
        low_threshold: Low voltage threshold
    """
    logger.section("Testing Alarm Reset")
    
    try:
        # Check if alarm is currently active
        previous_alarm_state = get_previous_alarm_state(hass_url, hass_token, state_entity_id)
        logger.info(f"Previous alarm state: {previous_alarm_state}")
        
        if not previous_alarm_state:
            logger.warning("Alarm is not currently active. Activating it for test...")
            set_alarm_state(hass_url, hass_token, state_entity_id, True)
            previous_alarm_state = True
            logger.info("Alarm state activated for test")
        
        # Get simulated low voltage
        current_voltage = get_uni_voltage(hass_url, hass_token, "")
        
        logger.info(f"Current voltage: {current_voltage}V, Low threshold: {low_threshold}V")
        
        # Check voltage against threshold for reset
        if current_voltage <= low_threshold and previous_alarm_state:
            logger.info(f"RESET: Voltage ({current_voltage}V) is below reset threshold ({low_threshold}V)")
            logger.info("✅ RESET CONDITION MET: Voltage below threshold and previously alarmed")
            
            # Send reset notification
            message = f"✅ RESET: Voltage level is {current_voltage}V, which is below the reset threshold of {low_threshold}V"
            success = send_telegram(message, hass_token, title="Voltage Alarm Reset")
            
            if success:
                logger.info("Reset notification sent successfully")
                # Update previous state
                set_alarm_state(hass_url, hass_token, state_entity_id, False)
                logger.info("Alarm state reset to False")
                return True
            else:
                logger.error("Failed to send reset notification")
                return False
        else:
            logger.info("Reset conditions not met")
            if not (current_voltage <= low_threshold):
                logger.info("❌ Voltage is not below threshold")
            if not previous_alarm_state:
                logger.info("❌ Alarm was not previously active")
            return True
            
    except Exception as e:
        logger.error(f"Error testing alarm reset: {str(e)}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 3:
        logger.error("Usage: test_alarm_reset.py <hass_token> <state_entity_id>")
        return
    
    token = sys.argv[1]
    state_entity_id = sys.argv[2]
    hass_url = "http://localhost:8123"
    
    # Run the test
    success = test_alarm_reset(hass_url, token, state_entity_id)
    
    if success:
        logger.info("✅ Alarm reset test completed successfully")
    else:
        logger.error("❌ Alarm reset test failed")

if __name__ == "__main__":
    main()
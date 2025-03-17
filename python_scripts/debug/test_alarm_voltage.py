#!/usr/bin/env python3
"""
Direct test for alarm voltage functionality
"""
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from services.alarm_voltage_measure import check_voltage_alarm
from common import get_logger

# Set up logger
logger = get_logger("test_alarm_voltage")

def main():
    """Run alarm voltage check directly"""
    if len(sys.argv) < 3:
        logger.error("Usage: test_alarm_voltage.py <hass_token> <entity_id> [state_entity_id]")
        return
        
    token = sys.argv[1]
    entity_id = sys.argv[2]
    hass_url = "http://localhost:8123"
    
    state_entity = None
    if len(sys.argv) > 3:
        state_entity = sys.argv[3]
    
    logger.info(f"Testing alarm voltage with entity: {entity_id}")
    logger.info(f"State entity: {state_entity}")
    
    success = check_voltage_alarm(hass_url, token, entity_id, state_entity)
    
    if success:
        logger.info("✅ Alarm voltage check completed successfully")
    else:
        logger.error("❌ Alarm voltage check failed")

if __name__ == "__main__":
    main()
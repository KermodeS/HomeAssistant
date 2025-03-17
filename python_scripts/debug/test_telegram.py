#!/usr/bin/env python3
"""
Test Telegram notifications for debugging
"""
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now import the common modules
from common import get_logger, send_telegram

# Set up logger
logger = get_logger("test_telegram")

def main():
    """Send a test Telegram message"""
    if len(sys.argv) < 2:
        logger.error("Usage: test_telegram.py <hass_token>")
        return
        
    token = sys.argv[1]
    logger.info("Sending test message to Telegram")
    
    success = send_telegram(
        "🧪 This is a test message from the voltage alarm system",
        token,
        title="Voltage Alarm Test"
    )
    
    if success:
        logger.info("✅ Message sent successfully")
    else:
        logger.error("❌ Failed to send message")

if __name__ == "__main__":
    main()
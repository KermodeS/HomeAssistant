#!/usr/bin/env python3
"""
Telegram debug utilities for Home Assistant
Provides functions for testing Telegram connectivity
"""
import sys
import os
import requests
import datetime
import traceback

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    
try:
    from common import get_logger
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current path: {sys.path}")
    
    # Fallback logger
    class SimpleLogger:
        def __init__(self, name):
            self.name = name
        def section(self, title):
            print(f"===== {title} =====")
        def info(self, message):
            print(f"[INFO] {message}")
        def error(self, message):
            print(f"[ERROR] {message}")
    
    get_logger = lambda name: SimpleLogger(name)
# Set up logger
logger = get_logger("telegram_debug")


def test_telegram(message, hass_token, hass_url="http://localhost:8123"):
    """
    Send a test message to Telegram
    
    Args:
        message: Message to send
        hass_token: Home Assistant long-lived access token
        hass_url: Home Assistant URL
        
    Returns:
        bool: Success status
    """
    logger.section("Testing Telegram Messaging")
    
    if not message:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"🧪 Test message from Home Assistant at {timestamp}"
    
    if not hass_token:
        logger.error("No Home Assistant token provided")
        return False
    
    try:
        url = f"{hass_url}/api/services/telegram_bot/send_message"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "message": message,
        }
        
        logger.info(f"Sending message: {message}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response text: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ Test message sent successfully!")
            return True
        else:
            logger.error("❌ Failed to send test message.")
            return False
            
    except Exception as e:
        logger.error(f"Error sending Telegram message: {str(e)}")
        return False


def test_telegram_formatting(hass_token, hass_url="http://localhost:8123"):
    """
    Test different formatting options in Telegram
    
    Args:
        hass_token: Home Assistant long-lived access token
        hass_url: Home Assistant URL
        
    Returns:
        bool: Success status
    """
    logger.section("Testing Telegram Formatting")
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Markdown message
        markdown_message = (
            f"*Telegram Formatting Test*\n\n"
            f"_Timestamp: {timestamp}_\n\n"
            f"*Bold text*\n"
            f"_Italic text_\n"
            f"`Monospace text`\n"
            f"[Link text](https://example.com)\n\n"
            f"• Bullet point 1\n"
            f"• Bullet point 2\n"
        )
        
        url = f"{hass_url}/api/services/telegram_bot/send_message"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "message": markdown_message,
            "data": {
                "parse_mode": "markdown"
            }
        }
        
        logger.info("Sending markdown-formatted message")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Markdown test message sent successfully!")
            return True
        else:
            logger.error(f"❌ Failed to send markdown test message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing Telegram formatting: {str(e)}")
        return False


def main():
    """Main function when run as a script"""
    # Get command line arguments
    if len(sys.argv) < 2:
        print("Usage: telegram_debug.py <hass_token> [message] [test_type]")
        print("  test_type: simple, format (default: simple)")
        return
    
    hass_token = sys.argv[1]
    hass_url = "http://localhost:8123"
    
    # Get message if provided
    message = f"🧪 Telegram test at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if len(sys.argv) > 2:
        message = sys.argv[2]
    
    # Determine which test to run
    test_type = "simple"
    if len(sys.argv) > 3:
        test_type = sys.argv[3].lower()
    
    if test_type == "simple":
        test_telegram(message, hass_token, hass_url)
    elif test_type == "format":
        test_telegram_formatting(hass_token, hass_url)
    else:
        logger.error(f"Unknown test type: {test_type}")
    
    logger.section("Telegram Test Complete")


if __name__ == "__main__":
    main()
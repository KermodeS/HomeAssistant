#!/usr/bin/env python3
"""
Notification system for Home Assistant automations
Supports Telegram and could be extended to other notification methods
"""
import requests
import datetime
import os
import logging
from .config_manager import config_manager
from .logger import get_logger

# Set up logger
logger = get_logger("notification")


class NotificationManager:
    """Handles sending notifications through various channels"""
    
    def __init__(self, hass_url="http://localhost:8123"):
        """
        Initialize the notification manager
        
        Args:
            hass_url: URL of the Home Assistant instance
        """
        self.hass_url = hass_url
        # Debug the config manager state
        logger.debug(f"Config manager: {config_manager}")
        
        # Check if telegram is enabled, with debug logging
        try:
            self.telegram_enabled = config_manager.get_config_value('notifications.telegram_enabled', False)
            logger.debug(f"Telegram enabled from config: {self.telegram_enabled}")
        except Exception as e:
            logger.error(f"Error getting telegram_enabled from config: {str(e)}")
            self.telegram_enabled = True  # Default to enabled if config fails
        
        # Log to file setting
        try:
            self.log_to_file = config_manager.get_config_value('notifications.log_to_file', True)
            logger.debug(f"Log to file from config: {self.log_to_file}")
        except Exception as e:
            logger.error(f"Error getting log_to_file from config: {str(e)}")
            self.log_to_file = True  # Default to enabled if config fails
            
        self.log_dir = "/config/www/logs"
        
        # Create log directory if needed and using file logging
        if self.log_to_file and not os.path.exists(self.log_dir):
            try:
                os.makedirs(self.log_dir)
            except Exception as e:
                logger.error(f"Error creating notification log directory: {str(e)}")
    
    def send_telegram(self, message, hass_token, markdown=True, title=None):
        """
        Send a message via Telegram using Home Assistant
        
        Args:
            message: The message to send
            hass_token: Long-lived access token for Home Assistant
            markdown: Whether to use markdown formatting
            title: Optional title for the message
            
        Returns:
            bool: Success status
        """
        # Force enable telegram for now for debugging
        #self.telegram_enabled = True
        
        logger.info(f"Telegram enabled setting: {self.telegram_enabled}")
        
        if not self.telegram_enabled:
            logger.info("Telegram notifications are disabled in configuration")
            return False
        
        if not hass_token:
            logger.error("No Home Assistant token provided")
            return False
        
        try:
            # Log the message if enabled
            if self.log_to_file:
                self._log_notification("telegram", message)
            
            # Add title if specified
            if title:
                message = f"*{title}*\n\n{message}" if markdown else f"{title}\n\n{message}"
            
            # Use the notify service
            url = f"{self.hass_url}/api/services/notify/kermode"
            headers = {
                "Authorization": f"Bearer {hass_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "message": message
            }
            
            # Add markdown parsing if enabled
            if markdown:
                data["data"] = {"parse_mode": "markdown"}
            
            logger.info(f"Sending Telegram notification: {message[:50]}...")
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram notification sent successfully")
                return True
            else:
                logger.error(f"Error sending Telegram notification: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Exception sending Telegram notification: {str(e)}")
            return False
    
    def _log_notification(self, channel, message):
        """
        Log a notification to file
        
        Args:
            channel: Notification channel (e.g., 'telegram')
            message: The message content
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file = f"{self.log_dir}/notifications.log"
            
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [{channel}] {message}\n\n")
                
        except Exception as e:
            logger.error(f"Error logging notification: {str(e)}")


# Create a singleton instance
notification_manager = NotificationManager()


def send_telegram(message, hass_token, markdown=True, title=None):
    """
    Convenience function to send a Telegram message
    
    Args:
        message: The message to send
        hass_token: Home Assistant access token
        markdown: Whether to use markdown formatting
        title: Optional title for the message
        
    Returns:
        bool: Success status
    """
    # For debugging/testing, force allow sending telegram messages
    global notification_manager
#    notification_manager.telegram_enabled = True
#    logger.info("Forcing telegram enabled for testing")
    
    return notification_manager.send_telegram(message, hass_token, markdown, title)


if __name__ == "__main__":
    # Test the notification system
    print("To test Telegram notification, run with a valid Home Assistant token")
    print("Usage: python3 -m common.notification <token>")
    
    import sys
    if len(sys.argv) > 1:
        token = sys.argv[1]
        test_message = "🧪 Test message from notification module"
        result = send_telegram(test_message, token)
        print(f"Notification sent: {result}")
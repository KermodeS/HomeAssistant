#!/usr/bin/env python3
"""
Simple test script to verify Telegram messaging is working
"""
import requests
import sys
import datetime

def send_telegram(message, hass_token):
    """Send a test message to Telegram"""
    try:
        url = "http://localhost:8123/api/services/telegram_bot/send_message"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "message": message
        }
        
        print(f"Sending message: {message}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Get token from command line
    if len(sys.argv) < 2:
        print("Usage: test_script.py <hass_token>")
        sys.exit(1)
    
    hass_token = sys.argv[1]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    test_message = f"🧪 Test message from Grocy script at {timestamp}"
    
    success = send_telegram(test_message, hass_token)
    
    if success:
        print("✅ Test message sent successfully!")
    else:
        print("❌ Failed to send test message.")
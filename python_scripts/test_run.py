#!/usr/bin/env python3
"""
Simple test script to verify basic functionality
"""
import sys
import requests
import datetime

# Create a log file to track execution
with open("/config/www/logs/test_run.log", "a") as f:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"\n\n{timestamp}: Test script started\n")
    
    # Log arguments
    f.write(f"{timestamp}: Number of arguments: {len(sys.argv)}\n")
    for i, arg in enumerate(sys.argv):
        if i == 1 and "token" in sys.argv[i-1].lower():  # Don't log the actual token
            f.write(f"{timestamp}: Argument {i}: [TOKEN REDACTED]\n")
        else:
            f.write(f"{timestamp}: Argument {i}: {arg}\n")
    
    try:
        # Try to send a test notification if token is provided
        if len(sys.argv) > 1:
            token = sys.argv[1]
            
            # Use the Home Assistant API to send a notification
            url = "http://localhost:8123/api/services/telegram_bot/send_message"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "message": f"🧪 Test message at {timestamp}"
            }
            
            f.write(f"{timestamp}: Attempting to send test message\n")
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            f.write(f"{timestamp}: Response status: {response.status_code}\n")
            if response.status_code == 200:
                f.write(f"{timestamp}: Message sent successfully\n")
            else:
                f.write(f"{timestamp}: Failed to send message: {response.text}\n")
        else:
            f.write(f"{timestamp}: No token provided, skipping notification test\n")
            
    except Exception as e:
        f.write(f"{timestamp}: Error: {str(e)}\n")
        print(f"Error: {str(e)}")
        sys.exit(1)

print("Test script completed. Check log for details.")
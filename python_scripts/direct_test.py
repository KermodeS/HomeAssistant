#!/usr/bin/env python3
"""
Direct test script to check token functionality
"""
import sys
import requests
import datetime

# Create log file
with open("/config/www/logs/direct_test.log", "a") as f:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"\n\n{timestamp}: Direct test started\n")
    
    # Make sure we have the token
    if len(sys.argv) < 2:
        f.write(f"{timestamp}: ERROR - No token provided\n")
        print("ERROR: No token provided")
        sys.exit(1)
    
    token = sys.argv[1]
    f.write(f"{timestamp}: Token received (first 5 chars): {token[:5]}...\n")
    
    try:
        # Use the Home Assistant API to send a notification
        url = "http://localhost:8123/api/services/telegram_bot/send_message"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "message": f"🔑 Direct token test at {timestamp}"
        }
        
        f.write(f"{timestamp}: Sending test message...\n")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        f.write(f"{timestamp}: Response status: {response.status_code}\n")
        if response.status_code == 200:
            f.write(f"{timestamp}: SUCCESS! Message sent\n")
            print("SUCCESS: Token works correctly")
        else:
            f.write(f"{timestamp}: FAILED: {response.text}\n")
            print(f"FAILED: Status {response.status_code}")
            
    except Exception as e:
        f.write(f"{timestamp}: ERROR: {str(e)}\n")
        print(f"ERROR: {str(e)}")
        sys.exit(1)
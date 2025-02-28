#!/usr/bin/env python3
"""
Debug script for Grocy API connection
"""
import sys
import datetime
import requests

# Create a log file to track execution
with open("/config/www/grocy_debug.log", "a") as f:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"\n\n{timestamp}: Debug script started\n")
    
    # Check arguments
    f.write(f"{timestamp}: Number of arguments: {len(sys.argv)}\n")
    for i, arg in enumerate(sys.argv):
        f.write(f"{timestamp}: Argument {i}: {arg}\n")
    
    # Check if we have enough arguments
    if len(sys.argv) < 3:
        f.write(f"{timestamp}: Not enough arguments. Need URL and API key.\n")
        print("Error: Not enough arguments. Need URL and API key.")
        sys.exit(1)
        
    grocy_url = sys.argv[1]
    grocy_api_key = sys.argv[2]
    
    f.write(f"{timestamp}: Using Grocy URL: {grocy_url}\n")
    f.write(f"{timestamp}: Using API Key: {grocy_api_key[:5]}...(truncated)\n")
    
    # Try to connect to Grocy API
    try:
        f.write(f"{timestamp}: Making API request...\n")
        
        headers = {
            "GROCY-API-KEY": grocy_api_key,
            "Content-Type": "application/json"
        }
        
        # Make sure the URL is properly formatted
        if not grocy_url.endswith("/"):
            grocy_url += "/"
            
        f.write(f"{timestamp}: Full URL: {grocy_url}\n")
        
        # Make the request with a 10 second timeout
        response = requests.get(grocy_url, headers=headers, timeout=10)
        
        f.write(f"{timestamp}: Response status code: {response.status_code}\n")
        f.write(f"{timestamp}: Response headers: {response.headers}\n")
        f.write(f"{timestamp}: Response content (first 500 chars): {response.text[:500]}\n")
        
        print(f"Grocy API Response: {response.status_code}")
        
    except Exception as e:
        f.write(f"{timestamp}: Error connecting to Grocy API: {str(e)}\n")
        print(f"Error connecting to Grocy API: {str(e)}")
        sys.exit(1)
        
print("Debug script completed successfully")
#!/usr/bin/env python3
"""
Improved debug script for Grocy API connection
"""
import sys
import datetime
import requests
import json

# Create a log file to track execution
with open("/config/www/grocy_debug.log", "a") as f:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"\n\n{timestamp}: Improved debug script started\n")
    
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
        headers = {
            "GROCY-API-KEY": grocy_api_key,
            "Content-Type": "application/json"
        }
        
        # Make sure the URL is properly formatted for API
        # The URL might need different formatting depending on your Grocy setup
        base_url = grocy_url
        if not base_url.endswith("/"):
            base_url += "/"
            
        # Try different API endpoints
        endpoints = [
            "",  # Base URL
            "api/",  # API root
            "api/objects/chores",  # Chores objects (v1 API)
            "api/chores",  # Chores endpoint (v2 API)
            "api/system/info"  # System info - should work on all versions
        ]
        
        f.write(f"{timestamp}: Testing multiple endpoints with base URL: {base_url}\n")
        
        for endpoint in endpoints:
            try:
                full_url = base_url + endpoint
                f.write(f"{timestamp}: Testing endpoint: {full_url}\n")
                
                # Try GET method
                get_response = requests.get(full_url, headers=headers, timeout=10)
                f.write(f"{timestamp}: GET {full_url} - Status: {get_response.status_code}\n")
                
                # If successful, log more details
                if get_response.status_code == 200:
                    f.write(f"{timestamp}: GET successful! Response preview: {get_response.text[:200]}...\n")
                    print(f"Success! Found working endpoint: {full_url}")
                    
                    # Try to parse as JSON to see the structure
                    try:
                        json_data = json.loads(get_response.text)
                        f.write(f"{timestamp}: JSON structure keys: {json.dumps(list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict')}\n")
                    except:
                        f.write(f"{timestamp}: Response is not valid JSON\n")
                
            except Exception as e:
                f.write(f"{timestamp}: Error with endpoint {full_url}: {str(e)}\n")
        
    except Exception as e:
        f.write(f"{timestamp}: General error connecting to Grocy API: {str(e)}\n")
        print(f"Error connecting to Grocy API: {str(e)}")
        sys.exit(1)
        
print("Improved debug script completed. Check log for details.")
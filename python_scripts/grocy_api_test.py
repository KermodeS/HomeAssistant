#!/usr/bin/env python3
"""
Grocy API test script specifically for your setup
"""
import sys
import datetime
import requests
import json

# Create log file
with open("/config/www/grocy_debug.log", "a") as f:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"\n\n{timestamp}: Focused API test started\n")
    
    # Get base URL from the provided URL
    if len(sys.argv) < 3:
        f.write(f"{timestamp}: Not enough arguments. Need URL and API key.\n")
        print("Error: Not enough arguments")
        sys.exit(1)
    
    # Extract the base URL up to the domain and port
    full_url = sys.argv[1]
    grocy_api_key = sys.argv[2]
    
    # Find the base domain and port
    parts = full_url.split('/')
    if len(parts) >= 3:
        base_url = '/'.join(parts[:3])  # http://192.168.1.128:9192
    else:
        base_url = full_url
    
    f.write(f"{timestamp}: Original URL: {full_url}\n")
    f.write(f"{timestamp}: Base URL extracted: {base_url}\n")
    
    # Test with common API endpoints
    test_endpoints = [
        "/",
        "/api",
        "/api/",
        "/api/objects/chores",
        "/api/chores",
        "/api/system/info",
        "/api/objects/chores/get-all",
        "/api/chores/get-all",
        "/api/objects/tasks",
        "/objects/chores",
        "/api/tasks"
    ]
    
    headers = {
        "GROCY-API-KEY": grocy_api_key,
        "Content-Type": "application/json"
    }
    
    # Test each endpoint
    for endpoint in test_endpoints:
        test_url = base_url + endpoint
        f.write(f"{timestamp}: Testing: {test_url}\n")
        
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            status = response.status_code
            f.write(f"{timestamp}: Status: {status}\n")
            
            if status == 200:
                f.write(f"{timestamp}: SUCCESS! Response preview: {response.text[:200]}\n")
                print(f"SUCCESS: Found working endpoint {test_url}")
                
                # Try to parse as JSON
                try:
                    data = json.loads(response.text)
                    if isinstance(data, list) and len(data) > 0:
                        f.write(f"{timestamp}: Found {len(data)} items\n")
                        # Print first item structure
                        if len(data) > 0 and isinstance(data[0], dict):
                            f.write(f"{timestamp}: First item keys: {list(data[0].keys())}\n")
                    elif isinstance(data, dict):
                        f.write(f"{timestamp}: Data keys: {list(data.keys())}\n")
                except:
                    f.write(f"{timestamp}: Response is not valid JSON\n")
            elif status == 405:
                # Try OPTIONS method for 405 responses
                try:
                    options_response = requests.options(test_url, headers=headers, timeout=10)
                    f.write(f"{timestamp}: OPTIONS method status: {options_response.status_code}\n")
                    if options_response.status_code == 200:
                        f.write(f"{timestamp}: OPTIONS successful, allowed methods: {options_response.headers.get('Allow', 'Not specified')}\n")
                except Exception as e:
                    f.write(f"{timestamp}: Error with OPTIONS: {str(e)}\n")
                    
        except Exception as e:
            f.write(f"{timestamp}: Error with {test_url}: {str(e)}\n")
    
    f.write(f"{timestamp}: Test completed\n")
    
print("Focused API test completed. Check the log for results.")
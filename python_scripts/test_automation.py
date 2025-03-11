#!/usr/bin/env python3
"""
Automation test utility
Can be run manually to verify all automations are working
"""
import os
import sys
import subprocess
import datetime

# Constants
SCRIPT_DIR = "/config/python_scripts"
LOG_DIR = "/config/www/logs"
TOKEN_PATH = "/config/token.txt"


def read_token():
    """Read Home Assistant token from file"""
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as f:
            return f.read().strip()
    return None


def test_grocy():
    """Test the Grocy module"""
    print("\n=== Testing Grocy Module ===")
    
    # Read token
    token = read_token()
    if not token:
        print("❌ Token not available")
        return False
    
    # Read grocy config from wrapper script (if possible)
    wrapper_path = f"{SCRIPT_DIR}/run_wrapper.sh"
    grocy_url = None
    grocy_api_key = None
    
    try:
        if os.path.exists(wrapper_path):
            with open(wrapper_path, 'r') as f:
                content = f.read()
                
                # Parse for --grocy-url
                if "--grocy-url" in content:
                    line = [l for l in content.split("\n") if "--grocy-url" in l][0]
                    if '"' in line:
                        grocy_url = line.split('"')[1]
                    elif "'" in line:
                        grocy_url = line.split("'")[1]
                
                # Parse for --grocy-api-key
                if "--grocy-api-key" in content:
                    line = [l for l in content.split("\n") if "--grocy-api-key" in l][0]
                    if '"' in line:
                        grocy_api_key = line.split('"')[1]
                    elif "'" in line:
                        grocy_api_key = line.split("'")[1]
    except Exception as e:
        print(f"⚠️ Error reading wrapper script: {str(e)}")
    
    # If we couldn't get it from wrapper, use defaults
    if not grocy_url:
        grocy_url = "http://192.168.1.128:9192"
        print(f"⚠️ Using default Grocy URL: {grocy_url}")
    
    if not grocy_api_key:
        grocy_api_key = "your-api-key"
        print(f"⚠️ Using default Grocy API key (likely won't work)")
    
    # Run the Grocy module
    log_file = f"{LOG_DIR}/grocy_test_manual.log"
    cmd = f"cd {SCRIPT_DIR} && python3 run.py --mode grocy --hass-token \"{token}\" --grocy-url \"{grocy_url}\" --grocy-api-key \"{grocy_api_key}\" --debug > \"{log_file}\" 2>&1"
    
    print(f"Running: {cmd}")
    try:
        start_time = datetime.datetime.now()
        exit_code = subprocess.call(cmd, shell=True)
        end_time = datetime.datetime.now()
        
        # Check result
        elapsed = (end_time - start_time).total_seconds()
        
        if exit_code == 0:
            print(f"✅ Grocy test completed successfully in {elapsed:.2f} seconds")
            
            # Check log file for more details
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_content = f.read()
                    
                    if "Sent notification with" in log_content:
                        lines = log_content.splitlines()
                        for line in lines:
                            if "Sent notification with" in line:
                                print(f"✅ {line}")
                                break
                    else:
                        print("⚠️ Notification may not have been sent")
            
            return True
        else:
            print(f"❌ Grocy test failed with exit code {exit_code}")
            
            # Show error from log
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_content = f.read()
                    
                    if "ERROR" in log_content:
                        lines = log_content.splitlines()
                        errors = [line for line in lines if "ERROR" in line]
                        for error in errors[-3:]:  # Show last 3 errors
                            print(f"❌ {error}")
            
            return False
    except Exception as e:
        print(f"❌ Error running Grocy test: {str(e)}")
        return False


def test_weather():
    """Test the Weather module"""
    print("\n=== Testing Weather Module ===")
    
    # Read token
    token = read_token()
    if not token:
        print("❌ Token not available")
        return False
    
    # Get weather entity
    weather_entity = "weather.openweathermap"
    
    # Run the Weather module
    log_file = f"{LOG_DIR}/weather_test_manual.log"
    cmd = f"cd {SCRIPT_DIR} && python3 run.py --mode weather --hass-token \"{token}\" --weather-entity \"{weather_entity}\" --debug > \"{log_file}\" 2>&1"
    
    print(f"Running: {cmd}")
    try:
        start_time = datetime.datetime.now()
        exit_code = subprocess.call(cmd, shell=True)
        end_time = datetime.datetime.now()
        
        elapsed = (end_time - start_time).total_seconds()
        
        if exit_code == 0:
            print(f"✅ Weather test completed successfully in {elapsed:.2f} seconds")
            
            # Check log file for more details
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_content = f.read()
                    
                    if "Sent temperature forecast notification" in log_content:
                        print("✅ Temperature forecast notification sent")
                    else:
                        print("⚠️ Temperature forecast notification may not have been sent")
            
            return True
        else:
            print(f"❌ Weather test failed with exit code {exit_code}")
            
            # Show error from log
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_content = f.read()
                    
                    if "ERROR" in log_content:
                        lines = log_content.splitlines()
                        errors = [line for line in lines if "ERROR" in line]
                        for error in errors[-3:]:  # Show last 3 errors
                            print(f"❌ {error}")
            
            return False
    except Exception as e:
        print(f"❌ Error running Weather test: {str(e)}")
        return False


def test_devices():
    """Test the Devices module"""
    print("\n=== Testing Devices Module ===")
    
    # Read token
    token = read_token()
    if not token:
        print("❌ Token not available")
        return False
    
    # Set device entity
    device_entity = "switch.shelly_caldaia"
    
    # Run the Devices module
    log_file = f"{LOG_DIR}/devices_test_manual.log"
    cmd = f"cd {SCRIPT_DIR} && python3 run.py --mode device --hass-token \"{token}\" --device-entity \"{device_entity}\" --device-state on --debug > \"{log_file}\" 2>&1"
    
    print(f"Running: {cmd}")
    try:
        start_time = datetime.datetime.now()
        exit_code = subprocess.call(cmd, shell=True)
        end_time = datetime.datetime.now()
        
        elapsed = (end_time - start_time).total_seconds()
        
        if exit_code == 0:
            print(f"✅ Devices test completed successfully in {elapsed:.2f} seconds")
            return True
        else:
            print(f"❌ Devices test failed with exit code {exit_code}")
            
            # Show error from log
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_content = f.read()
                    
                    if "ERROR" in log_content:
                        lines = log_content.splitlines()
                        errors = [line for line in lines if "ERROR" in line]
                        for error in errors[-3:]:  # Show last 3 errors
                            print(f"❌ {error}")
            
            return False
    except Exception as e:
        print(f"❌ Error running Devices test: {str(e)}")
        return False


def main():
    """Main function"""
    print("=== Home Assistant Automation Test ===")
    print(f"Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        if test_name == "grocy":
            test_grocy()
        elif test_name == "weather":
            test_weather()
        elif test_name == "devices":
            test_devices()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: grocy, weather, devices")
    else:
        # Run all tests
        results = {}
        results["grocy"] = test_grocy()
        results["weather"] = test_weather()
        results["devices"] = test_devices()
        
        # Print summary
        print("\n=== Test Summary ===")
        for name, result in results.items():
            print(f"{name}: {'✅ Passed' if result else '❌ Failed'}")
    
    print(f"\nTest completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Automation diagnostics tool
Checks for common issues with automations and services
"""
import os
import sys
import subprocess
import datetime
import json
import requests
import time

# Constants
LOG_DIR = "/config/www/logs"
CONFIG_DIR = "/config/python_scripts"
AUTOMATION_MODULES = ["grocy", "weather", "devices"]


def run_command(command, capture_output=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=False,
            capture_output=capture_output,
            text=True
        )
        return result
    except Exception as e:
        print(f"Error running command '{command}': {str(e)}")
        return None


def check_file_permissions():
    """Check file permissions for key files"""
    print("\n=== Checking File Permissions ===")
    
    files_to_check = [
        "/config/python_scripts/run.py",
        "/config/python_scripts/run_wrapper.sh",
        "/config/token.txt"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            stat_info = os.stat(file_path)
            mode = stat_info.st_mode
            
            # Check if executable
            is_executable = bool(mode & 0o100)  # Owner has execute permission
            
            # Check if readable
            is_readable = bool(mode & 0o400)    # Owner has read permission
            
            print(f"{file_path}: {'✅' if is_readable else '❌'} Readable, {'✅' if is_executable else '❌'} Executable")
            
            if not is_executable and file_path.endswith(('.py', '.sh')):
                print(f"  Setting executable permission on {file_path}")
                os.chmod(file_path, mode | 0o100)
        else:
            print(f"{file_path}: ❌ File not found")


def check_token():
    """Check if token file exists and contains valid data"""
    print("\n=== Checking Token ===")
    
    token_path = "/config/token.txt"
    
    if os.path.exists(token_path):
        try:
            with open(token_path, 'r') as f:
                token = f.read().strip()
                
            if token:
                token_length = len(token)
                if token_length > 20:
                    print(f"✅ Token exists and has sufficient length ({token_length} chars)")
                    
                    # Test API call
                    try:
                        api_url = "http://localhost:8123/api/config"
                        headers = {
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json"
                        }
                        
                        response = requests.get(api_url, headers=headers, timeout=10)
                        
                        if response.status_code == 200:
                            print("✅ Token successfully authenticated with Home Assistant API")
                        else:
                            print(f"❌ Token authentication failed: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Error testing token with API: {str(e)}")
                else:
                    print(f"❌ Token seems too short ({token_length} chars)")
            else:
                print("❌ Token file is empty")
        except Exception as e:
            print(f"❌ Error reading token file: {str(e)}")
    else:
        print(f"❌ Token file not found at {token_path}")


def check_configuration():
    """Check feature flags configuration"""
    print("\n=== Checking Feature Flags ===")
    
    config_path = f"{CONFIG_DIR}/feature_flags.yaml"
    
    if os.path.exists(config_path):
        try:
            # Try to import YAML
            import yaml
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if config:
                print(f"✅ Configuration loaded with {len(config)} sections")
                
                # Check specific sections
                for module in AUTOMATION_MODULES:
                    if module in config:
                        enabled = config[module].get('enabled', False)
                        print(f"  {module}: {'✅ Enabled' if enabled else '❌ Disabled'}")
                        
                        # Show specific features
                        for feature, value in config[module].items():
                            if feature != 'enabled':
                                print(f"    - {feature}: {'✅ Enabled' if value else '❌ Disabled'}")
                    else:
                        print(f"  {module}: ❌ Section not found")
                
                # Check notification configuration
                if 'notifications' in config:
                    print(f"  notifications:")
                    for key, value in config['notifications'].items():
                        print(f"    - {key}: {'✅ Enabled' if value else '❌ Disabled'}")
            else:
                print("❌ Configuration is empty")
        except ImportError:
            print("❌ Cannot import yaml module")
            
            # Simple string-based check
            with open(config_path, 'r') as f:
                content = f.read()
                
            for module in AUTOMATION_MODULES:
                if f"{module}:" in content:
                    enabled = "enabled: true" in content.split(f"{module}:")[1].split("\n")[1]
                    print(f"  {module}: {'✅ Enabled' if enabled else '❌ Disabled'}")
        except Exception as e:
            print(f"❌ Error checking configuration: {str(e)}")
    else:
        print(f"❌ Configuration file not found at {config_path}")


def check_logs():
    """Check log files for errors"""
    print("\n=== Checking Log Files ===")
    
    log_files = {
        "grocy.log": "Grocy module",
        "weather.log": "Weather module",
        "devices.log": "Device monitoring",
        "main.log": "Main application",
        "wrapper.log": "Wrapper script"
    }
    
    for log_file, description in log_files.items():
        log_path = f"{LOG_DIR}/{log_file}"
        
        if os.path.exists(log_path):
            # Get file size and last modified time
            size = os.path.getsize(log_path)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(log_path))
            
            print(f"{log_file} ({description}):")
            print(f"  Size: {size/1024:.1f}KB, Last modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check recent errors
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    last_lines = lines[-50:] if len(lines) >= 50 else lines
                    
                    error_count = sum(1 for line in last_lines if "[ERROR]" in line or "Error" in line)
                    if error_count > 0:
                        print(f"  ❌ Found {error_count} errors in recent log entries")
                        
                        # Show the errors
                        print("  Recent errors:")
                        for line in last_lines:
                            if "[ERROR]" in line or "Error" in line:
                                print(f"    {line.strip()}")
                    else:
                        print("  ✅ No recent errors found")
            except Exception as e:
                print(f"  ❌ Error reading log file: {str(e)}")
        else:
            print(f"{log_file}: ❌ Log file not found")


def test_automation(module):
    """Test a specific automation module"""
    print(f"\n=== Testing {module.title()} Module ===")
    
    # Get token
    token_path = "/config/token.txt"
    if not os.path.exists(token_path):
        print(f"❌ Cannot test {module} module: Token file not found")
        return
    
    with open(token_path, 'r') as f:
        token = f.read().strip()
    
    if not token:
        print(f"❌ Cannot test {module} module: Token is empty")
        return
    
    # Prepare command based on module
    if module == "grocy":
        # Get Grocy URL and API key
        grocy_url = None
        grocy_api_key = None
        
        try:
            # Try to get from Home Assistant API
            api_url = "http://localhost:8123/api/states/input_text.grocy_url"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                grocy_url = data.get("state")
            
            api_url = "http://localhost:8123/api/states/input_text.grocy_api_key"
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                grocy_api_key = data.get("state")
        except Exception as e:
            print(f"❌ Error getting Grocy details from API: {str(e)}")
        
        if not grocy_url or not grocy_api_key:
            print("❌ Cannot test Grocy module: Missing URL or API key")
            return
        
        command = f"{CONFIG_DIR}/run.py --mode grocy --hass-token \"{token}\" --grocy-url \"{grocy_url}\" --grocy-api-key \"{grocy_api_key}\" --debug"
    
    elif module == "weather":
        command = f"{CONFIG_DIR}/run.py --mode weather --hass-token \"{token}\" --debug"
    
    elif module == "devices":
        # Get Shelly entity ID
        shelly_entity = None
        
        try:
            api_url = "http://localhost:8123/api/states/input_text.shelly_caldaia_entity"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                shelly_entity = data.get("state")
        except Exception as e:
            print(f"❌ Error getting Shelly entity from API: {str(e)}")
        
        if not shelly_entity:
            print("❌ Cannot test Devices module: Missing Shelly entity ID")
            return
        
        command = f"{CONFIG_DIR}/run.py --mode device --hass-token \"{token}\" --device-entity \"{shelly_entity}\" --device-state on --debug"
    
    else:
        print(f"❌ Unknown module: {module}")
        return
    
    # Run the command
    print(f"Running: python3 {command}")
    start_time = time.time()
    process = subprocess.Popen(
        f"cd {CONFIG_DIR} && python3 {command}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Set a timeout of 30 seconds
    timeout = 30
    output = ""
    error = ""
    
    try:
        output, error = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        print(f"❌ Test timed out after {timeout} seconds")
        try:
            output, error = process.communicate()
        except:
            pass
    
    elapsed_time = time.time() - start_time
    
    # Display results
    if process.returncode == 0:
        print(f"✅ Test completed successfully in {elapsed_time:.2f} seconds")
    else:
        print(f"❌ Test failed with exit code {process.returncode} in {elapsed_time:.2f} seconds")
    
    if output:
        print("\nOutput:")
        # Print only the last 20 lines if it's too long
        output_lines = output.splitlines()
        if len(output_lines) > 20:
            output = "\n".join(output_lines[-20:])
            print(f"(Showing last 20 of {len(output_lines)} lines)")
        print(output)
    
    if error:
        print("\nErrors:")
        print(error)


def main():
    """Main function"""
    print("=== Home Assistant Automation Diagnostics ===")
    print(f"Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            if len(sys.argv) > 2:
                module = sys.argv[2].lower()
                if module in AUTOMATION_MODULES:
                    test_automation(module)
                elif module == "all":
                    for m in AUTOMATION_MODULES:
                        test_automation(m)
                else:
                    print(f"Unknown module: {module}")
                    print(f"Available modules: {', '.join(AUTOMATION_MODULES)}")
            else:
                print("Please specify a module to test")
                print(f"Available modules: {', '.join(AUTOMATION_MODULES)} or 'all'")
        elif command == "permissions":
            check_file_permissions()
        elif command == "token":
            check_token()
        elif command == "config":
            check_configuration()
        elif command == "logs":
            check_logs()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: test, permissions, token, config, logs")
    else:
        # Run all checks
        check_file_permissions()
        check_token()
        check_configuration()
        check_logs()
    
    print(f"\nDiagnostics completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
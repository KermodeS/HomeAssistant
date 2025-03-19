#!/usr/bin/env python3
"""
Debug script to check feature flag configuration
"""
import os
import sys
import yaml

# Add the parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def check_config_file():
    """Check the feature flags configuration file"""
    config_path = "/config/python_scripts/feature_flags.yaml"
    
    print(f"Checking configuration file: {config_path}")
    
    if os.path.exists(config_path):
        print(f"✅ Configuration file exists")
        
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                
            print("Configuration contents:")
            for section, values in config.items():
                print(f"  {section}:")
                for key, value in values.items():
                    print(f"    {key}: {value}")
                    
            # Check specific keys
            print("\nChecking specific flags:")
            
            # Check Telegram enabled flag
            telegram_enabled = config.get('notifications', {}).get('telegram_enabled', False)
            print(f"  notifications.telegram_enabled: {telegram_enabled}")
            
            # Check Grocy enabled flag
            grocy_enabled = config.get('grocy', {}).get('enabled', False)
            print(f"  grocy.enabled: {grocy_enabled}")
            
            # Check Grocy chores notification flag
            chores_notification = config.get('grocy', {}).get('chores_notification', False)
            print(f"  grocy.chores_notification: {chores_notification}")
            
        except Exception as e:
            print(f"❌ Error reading configuration: {str(e)}")
    else:
        print(f"❌ Configuration file does not exist")

if __name__ == "__main__":
    check_config_file()
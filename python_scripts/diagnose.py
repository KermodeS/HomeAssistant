#!/usr/bin/env python3
"""
Diagnostic tool for Home Assistant automation scripts
Helps identify common issues with the environment and configuration
"""
import os
import sys
import importlib.util
import traceback


def check_directory(path):
    """Check if a directory exists and list its contents"""
    print(f"\nChecking directory: {path}")
    
    if os.path.exists(path):
        print(f"✅ Directory exists: {path}")
        
        try:
            contents = os.listdir(path)
            print(f"📁 Contents ({len(contents)} items):")
            for item in sorted(contents):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    print(f"  📂 {item}/")
                else:
                    print(f"  📄 {item}")
        except Exception as e:
            print(f"❌ Error listing directory contents: {str(e)}")
    else:
        print(f"❌ Directory does not exist: {path}")


def check_file(path):
    """Check if a file exists and if it's readable"""
    print(f"\nChecking file: {path}")
    
    if os.path.exists(path):
        print(f"✅ File exists: {path}")
        
        try:
            # Check if readable
            with open(path, 'r') as f:
                first_line = f.readline().strip()
            print(f"✅ File is readable. First line: {first_line}")
            
            # Check permissions
            permissions = oct(os.stat(path).st_mode)[-3:]
            print(f"📝 File permissions: {permissions}")
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}")
    else:
        print(f"❌ File does not exist: {path}")


def check_python_import(module_name, path=None):
    """Try to import a module and report success/failure"""
    print(f"\nTrying to import: {module_name}")
    
    try:
        if path:
            # Import from specific file
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None:
                print(f"❌ Failed to create spec for {module_name} from {path}")
                return
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"✅ Successfully imported {module_name} from {path}")
        else:
            # Standard import
            module = importlib.import_module(module_name)
            print(f"✅ Successfully imported {module_name}")
            print(f"📍 Module location: {module.__file__}")
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        print(f"📋 Traceback:\n{traceback.format_exc()}")


def check_python_path():
    """Check the Python path (sys.path)"""
    print("\nChecking Python path (sys.path):")
    
    for i, path in enumerate(sys.path):
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"  {i}: {exists} {path}")


def print_system_info():
    """Print basic system information"""
    print("\n===== System Information =====")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")


def check_logs_directory():
    """Check the logs directory"""
    logs_dir = "/config/www/logs"
    
    print(f"\nChecking logs directory: {logs_dir}")
    
    if os.path.exists(logs_dir):
        print(f"✅ Logs directory exists: {logs_dir}")
        
        try:
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
            print(f"📄 Log files ({len(log_files)} files):")
            
            for log_file in sorted(log_files):
                log_path = os.path.join(logs_dir, log_file)
                size = os.path.getsize(log_path)
                print(f"  📄 {log_file} ({size} bytes)")
                
                # Show last 2 lines of each log file
                try:
                    with open(log_path, 'r') as f:
                        lines = f.readlines()
                        last_lines = lines[-2:] if len(lines) >= 2 else lines
                        print("    Last lines:")
                        for line in last_lines:
                            print(f"    > {line.strip()}")
                except Exception as e:
                    print(f"    Error reading log: {str(e)}")
        except Exception as e:
            print(f"❌ Error accessing logs: {str(e)}")
    else:
        print(f"❌ Logs directory does not exist: {logs_dir}")
        try:
            os.makedirs(logs_dir)
            print(f"✅ Created logs directory: {logs_dir}")
        except Exception as e:
            print(f"❌ Failed to create logs directory: {str(e)}")


def check_configuration():
    """Check the feature flags configuration"""
    config_path = "/config/python_scripts/feature_flags.yaml"
    
    print(f"\nChecking configuration file: {config_path}")
    
    if os.path.exists(config_path):
        print(f"✅ Configuration file exists: {config_path}")
        
        try:
            import yaml
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                
            print("📋 Configuration contents:")
            for section, values in config.items():
                print(f"  {section}:")
                for key, value in values.items():
                    print(f"    {key}: {value}")
        except ImportError:
            print("❌ YAML module not available, cannot parse configuration")
        except Exception as e:
            print(f"❌ Error reading configuration: {str(e)}")
    else:
        print(f"❌ Configuration file does not exist: {config_path}")


def main():
    """Run all diagnostic checks"""
    print("===== Home Assistant Automation Diagnostics =====")
    print(f"Started at: {os.popen('date').read().strip()}")
    
    # Check system information
    print_system_info()
    
    # Check Python path
    check_python_path()
    
    # Check key directories
    check_directory("/config/python_scripts")
    check_directory("/config/python_scripts/common")
    check_directory("/config/python_scripts/services")
    check_directory("/config/python_scripts/debug")
    
    # Check key files
    check_file("/config/python_scripts/run.py")
    check_file("/config/python_scripts/run_wrapper.sh")
    check_file("/config/python_scripts/feature_flags.yaml")
    
    # Check logs
    check_logs_directory()
    
    # Check configuration
    check_configuration()
    
    # Try importing key modules
    check_python_import("common.logger", "/config/python_scripts/common/logger.py")
    check_python_import("common.config_manager", "/config/python_scripts/common/config_manager.py")
    check_python_import("services.grocy", "/config/python_scripts/services/grocy.py")
    
    print("\n===== Diagnostics Complete =====")


if __name__ == "__main__":
    main()
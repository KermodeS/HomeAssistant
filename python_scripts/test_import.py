#!/usr/bin/env python3
"""Test script to check module imports"""
import sys
import os

# Add the current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"Python path: {sys.path}")
print(f"Current directory: {current_dir}")

try:
    # Try importing the module
    from services.grocy_dashboard import update_dashboard_data
    print("✅ Successfully imported grocy_dashboard module")
except ImportError as e:
    print(f"❌ Error importing module: {str(e)}")
    print(f"Detailed error: {type(e).__name__}: {str(e)}")
    
    # Try to find the file
    dashboard_path = os.path.join(current_dir, 'services', 'grocy_dashboard.py')
    if os.path.exists(dashboard_path):
        print(f"✅ File exists at: {dashboard_path}")
    else:
        print(f"❌ File not found at: {dashboard_path}")
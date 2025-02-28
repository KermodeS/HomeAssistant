#!/usr/bin/env python3
"""
Simple test script for Grocy integration
"""
import sys
import datetime

# Create a simple log file
with open("/config/www/grocy_test.log", "a") as f:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"{timestamp}: Test script executed\n")
    f.write(f"{timestamp}: Arguments: {sys.argv}\n")

print("Test script executed successfully")
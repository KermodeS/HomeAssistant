#!/usr/bin/env python3
"""
Grocy API debugging tool
Tests connections and API endpoints for troubleshooting
"""
import sys
import os
import requests
import json
import datetime

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from common.logger import get_logger
except ImportError:
    # Fallback logger if import fails
    class SimpleLogger:
        def __init__(self, name):
            self.name = name
            print(f"Created simple logger for {name}")
        
        def section(self, title):
            divider = "=" * len(title)
            print(f"\n{divider}\n{title}\n{divider}")
        
        def info(self, message):
            print(f"[INFO] {message}")
        
        def error(self, message):
            print(f"[ERROR] {message}")
        
        def debug(self, message):
            print(f"[DEBUG] {message}")
    
    get_logger = lambda name: SimpleLogger(name)

# Set up logger
logger = get_logger("grocy_debug")


def test_connection(grocy_url, grocy_api_key):
    """
    Test connection to Grocy API
    
    Args:
        grocy_url: Grocy API URL
        grocy_api_key: Grocy API key
    """
    logger.section("Testing Grocy Connection")
    
    # Remove trailing slash if present
    grocy_url = grocy_url.rstrip('/')
    
    logger.info(f"Using Grocy URL: {grocy_url}")
    
    # List of endpoints to test
    endpoints = [
        "",              # Base URL
        "/api/system/info",  # System info
        "/api/system/db-changed-time",  # DB change timestamp
        "/api/objects/chores"  # Chores
    ]
    
    headers = {
        "GROCY-API-KEY": grocy_api_key,
        "Content-Type": "application/json"
    }
    
    # Test each endpoint
    for endpoint in endpoints:
        test_url = f"{grocy_url}{endpoint}"
        logger.info(f"Testing endpoint: {test_url}")
        
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            
            logger.info(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                logger.info("✅ Connection successful")
                
                # Try to parse as JSON
                try:
                    data = response.json()
                    logger.info("✅ Response is valid JSON")
                    
                    # Print limited amount of data
                    if isinstance(data, dict):
                        logger.info(f"Keys: {', '.join(data.keys())}")
                    elif isinstance(data, list):
                        logger.info(f"Array with {len(data)} items")
                        
                except json.JSONDecodeError:
                    logger.info("Response is not JSON")
                    logger.debug(f"First 200 chars: {response.text[:200]}")
            else:
                logger.error(f"❌ Connection failed: {response.status_code}")
                logger.debug(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            logger.error(f"❌ Error connecting to {test_url}: {str(e)}")
    
    logger.section("Connection Test Complete")


def test_endpoints(grocy_url, grocy_api_key):
    """
    Test all known Grocy API endpoints
    
    Args:
        grocy_url: Grocy API URL
        grocy_api_key: Grocy API key
    """
    logger.section("Testing Grocy API Endpoints")
    
    # Remove trailing slash if present
    grocy_url = grocy_url.rstrip('/')
    
    # Define endpoints to test
    endpoints = [
        "/api/system/info",
        "/api/system/db-changed-time",
        "/api/users",
        "/api/objects/chores",
        "/api/chores",
        "/api/objects/products",
        "/api/objects/locations",
        "/api/objects/shopping_list",
        "/api/objects/tasks"
    ]
    
    headers = {
        "GROCY-API-KEY": grocy_api_key,
        "Content-Type": "application/json"
    }
    
    # Test each endpoint
    results = []
    for endpoint in endpoints:
        test_url = f"{grocy_url}{endpoint}"
        logger.info(f"Testing endpoint: {test_url}")
        
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            
            status = "✅" if response.status_code == 200 else "❌"
            results.append({
                "endpoint": endpoint,
                "status_code": response.status_code,
                "success": response.status_code == 200
            })
            
            logger.info(f"{status} Status code: {response.status_code}")
            
            if response.status_code == 200:
                # Try to parse as JSON
                try:
                    data = response.json()
                    
                    # Print summary of data
                    if isinstance(data, dict):
                        logger.info(f"Response contains {len(data.keys())} keys")
                    elif isinstance(data, list):
                        logger.info(f"Response contains {len(data)} items")
                    
                except json.JSONDecodeError:
                    logger.info("Response is not JSON")
            else:
                logger.error(f"Failed to access endpoint: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error testing endpoint {endpoint}: {str(e)}")
            results.append({
                "endpoint": endpoint,
                "status_code": -1,
                "success": False,
                "error": str(e)
            })
    
    # Print summary
    logger.section("Endpoints Summary")
    success_count = sum(1 for r in results if r.get("success", False))
    logger.info(f"Successful endpoints: {success_count}/{len(endpoints)}")
    
    failed = [r["endpoint"] for r in results if not r.get("success", False)]
    if failed:
        logger.info(f"Failed endpoints: {', '.join(failed)}")
    
    logger.section("Endpoint Testing Complete")


def test_chores(grocy_url, grocy_api_key):
    """
    Test chores API specifically and display results
    
    Args:
        grocy_url: Grocy API URL
        grocy_api_key: Grocy API key
    """
    logger.section("Testing Grocy Chores API")
    
    # Remove trailing slash if present
    grocy_url = grocy_url.rstrip('/')
    
    # Define chores-related endpoints
    endpoints = [
        "/api/chores",
        "/api/objects/chores"
    ]
    
    headers = {
        "GROCY-API-KEY": grocy_api_key,
        "Content-Type": "application/json"
    }
    
    # Test each endpoint and capture chores data
    chores_data = []
    for endpoint in endpoints:
        test_url = f"{grocy_url}{endpoint}"
        logger.info(f"Testing chores endpoint: {test_url}")
        
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully accessed {endpoint}")
                
                # Parse the data
                try:
                    data = response.json()
                    
                    if isinstance(data, list):
                        logger.info(f"Found {len(data)} items")
                        
                        # Store chores data for later display
                        chores_data.append({
                            "endpoint": endpoint,
                            "data": data
                        })
                        
                        # Print the first chore as an example
                        if data:
                            logger.info("Example chore data:")
                            example_chore = data[0]
                            
                            if isinstance(example_chore, dict):
                                for key, value in example_chore.items():
                                    if key in ["id", "name", "description"] or (
                                        "chore_name" in example_chore and 
                                        key in ["chore_name", "next_estimated_execution_time"]
                                    ):
                                        logger.info(f"  {key}: {value}")
                    else:
                        logger.info("Response is not a list")
                        
                except json.JSONDecodeError:
                    logger.error("Response is not valid JSON")
            else:
                logger.error(f"❌ Failed to access {endpoint}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error testing chores endpoint {endpoint}: {str(e)}")
    
    # Display a summary of chores if found
    if chores_data:
        logger.section("Chores Summary")
        
        for endpoint_data in chores_data:
            endpoint = endpoint_data["endpoint"]
            data = endpoint_data["data"]
            
            if not data:
                logger.info(f"No chores found at {endpoint}")
                continue
                
            logger.info(f"Chores from {endpoint}:")
            
            # Extract basic info based on the endpoint format
            if "/api/chores" in endpoint:
                # This is likely the /api/chores endpoint with extended data
                for i, chore in enumerate(data[:5]):  # Limit to 5 chores for readability
                    chore_name = chore.get("chore_name", "Unknown")
                    next_date = chore.get("next_estimated_execution_time", "Unknown")
                    assigned_to = "Unassigned"
                    
                    if "next_execution_assigned_user" in chore and chore["next_execution_assigned_user"]:
                        assigned_user = chore["next_execution_assigned_user"]
                        if isinstance(assigned_user, dict) and "display_name" in assigned_user:
                            assigned_to = assigned_user["display_name"]
                    
                    logger.info(f"  {i+1}. {chore_name} - Next: {next_date}, Assigned to: {assigned_to}")
                
                if len(data) > 5:
                    logger.info(f"  ... and {len(data) - 5} more chores")
            
            elif "/api/objects/chores" in endpoint:
                # This is likely the /api/objects/chores endpoint with basic data
                for i, chore in enumerate(data[:5]):  # Limit to 5 chores for readability
                    chore_name = chore.get("name", "Unknown")
                    period_type = chore.get("period_type", "Unknown")
                    
                    logger.info(f"  {i+1}. {chore_name} - Period type: {period_type}")
                
                if len(data) > 5:
                    logger.info(f"  ... and {len(data) - 5} more chores")
    
    logger.section("Chores Testing Complete")


def main():
    """Main function to run tests based on command line arguments"""
    if len(sys.argv) < 4:
        print("Usage: grocy_debug.py <grocy_url> <grocy_api_key> <test_type>")
        print("  test_type: connection, endpoints, chores")
        return
    
    grocy_url = sys.argv[1]
    grocy_api_key = sys.argv[2]
    test_type = sys.argv[3].lower()
    
    logger.section(f"Grocy Debug - {test_type.title()} Test")
    logger.info(f"Starting at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if test_type == "connection":
        test_connection(grocy_url, grocy_api_key)
    elif test_type == "endpoints":
        test_endpoints(grocy_url, grocy_api_key)
    elif test_type == "chores":
        test_chores(grocy_url, grocy_api_key)
    else:
        logger.error(f"Unknown test type: {test_type}")
        print("Valid test types: connection, endpoints, chores")
    
    logger.section("Debug Complete")


if __name__ == "__main__":
    main()
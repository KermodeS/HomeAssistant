#!/usr/bin/env python3
"""
Debug utility for weather forecast in Home Assistant
"""
import requests
import json
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from common.logger import get_logger
except ImportError:
    # Fallback logger
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
logger = get_logger("weather_debug")

def test_weather_entity(hass_url, hass_token, entity_id="weather.openweathermap"):
    """
    Test if a weather entity exists and get its state
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Weather entity ID
    """
    logger.section(f"Testing Weather Entity: {entity_id}")
    
    try:
        url = f"{hass_url}/api/states/{entity_id}"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Checking entity state at: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Entity exists")
            
            # Parse the state data
            state_data = response.json()
            state = state_data.get("state", "unknown")
            logger.info(f"Current state: {state}")
            
            # Check attributes
            attributes = state_data.get("attributes", {})
            logger.info(f"Attributes: {', '.join(attributes.keys())}")
            
            # Check for forecast in attributes
            if "forecast" in attributes:
                forecast = attributes["forecast"]
                logger.info(f"Forecast entries: {len(forecast)}")
                if forecast:
                    logger.info("First forecast entry:")
                    logger.info(json.dumps(forecast[0], indent=2))
            else:
                logger.error("❌ No forecast attribute found")
                
        else:
            logger.error(f"❌ Failed to get entity state: {response.status_code}")
            logger.debug(f"Response: {response.text}")
            
    except Exception as e:
        logger.error(f"Error testing weather entity: {str(e)}")

def test_forecast_service(hass_url, hass_token, entity_id="weather.openweathermap"):
    """
    Test the get_forecasts service
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Weather entity ID
    """
    logger.section("Testing get_forecasts service")
    
    try:
        url = f"{hass_url}/api/services/weather/get_forecasts?return_response"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "type": "daily",
            "entity_id": entity_id
        }
        
        logger.info(f"Calling service with {json.dumps(data)}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Service call successful")
            
            result = response.json()
            logger.info(f"Response contains data for: {', '.join(result.keys())}")
            
            if "service_response" in result:
                service_response = result["service_response"]
                logger.info(f"Service response keys: {', '.join(service_response.keys())}")
    
                if entity_id in service_response:
                    entity_data = service_response[entity_id]
                logger.info(f"Entity data keys: {', '.join(entity_data.keys())}")
                
                if "forecast" in entity_data:
                    forecast = entity_data["forecast"]
                    logger.info(f"Found {len(forecast)} forecast entries")
                    
                    if forecast and len(forecast) >= 3:
                        logger.info("✅ Sufficient forecast data available")
                        
                        # Show the first forecast entry
                        logger.info("First forecast entry:")
                        logger.info(json.dumps(forecast[0], indent=2))
                    else:
                        logger.error(f"❌ Insufficient forecast data: {len(forecast)} entries")
                else:
                    logger.error("❌ No forecast data in response")
            else:
                logger.error(f"❌ No data for entity {entity_id} in response")
                
        else:
            logger.error(f"❌ Service call failed: {response.status_code}")
            logger.debug(f"Response: {response.text}")
            
    except Exception as e:
        logger.error(f"Error testing forecast service: {str(e)}")

def list_weather_entities(hass_url, hass_token):
    """
    List all weather entities in Home Assistant
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
    """
    logger.section("Listing Weather Entities")
    
    try:
        url = f"{hass_url}/api/states"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Fetching all entities from: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            all_entities = response.json()
            logger.info(f"Found {len(all_entities)} total entities")
            
            weather_entities = [e for e in all_entities if e["entity_id"].startswith("weather.")]
            logger.info(f"Found {len(weather_entities)} weather entities:")
            
            for entity in weather_entities:
                entity_id = entity["entity_id"]
                state = entity["state"]
                source = entity.get("attributes", {}).get("attribution", "Unknown source")
                logger.info(f"  - {entity_id}: {state} ({source})")
                
        else:
            logger.error(f"❌ Failed to get entities: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error listing weather entities: {str(e)}")

def main():
    """Main function to run tests based on command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: weather_debug.py <hass_token> [entity_id] [test_type]")
        print("  test_type: entity, service, list (default: all)")
        return
    
    hass_token = sys.argv[1]
    hass_url = "http://localhost:8123"
    
    # Use custom entity_id if provided
    entity_id = "weather.openweathermap"
    if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        entity_id = sys.argv[2]
        
    # Determine which test to run
    test_type = "all"
    if len(sys.argv) > 3:
        test_type = sys.argv[3].lower()
        
    logger.section("Weather API Debug")
    
    if test_type == "entity" or test_type == "all":
        test_weather_entity(hass_url, hass_token, entity_id)
        
    if test_type == "service" or test_type == "all":
        test_forecast_service(hass_url, hass_token, entity_id)
        
    if test_type == "list" or test_type == "all":
        list_weather_entities(hass_url, hass_token)
        
    logger.section("Debug Complete")


if __name__ == "__main__":
    main()
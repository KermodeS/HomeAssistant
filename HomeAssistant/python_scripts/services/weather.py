#!/usr/bin/env python3
"""
Weather service module for Home Assistant
Extracts and processes weather data from OpenWeatherMap integration
"""
import requests
import datetime
import sys
import json
from common import get_logger, send_telegram, config_manager

# Set up logger
logger = get_logger("weather")


def get_forecast_data(hass_url, hass_token, entity_id="weather.openweathermap"):
    """
    Get forecast data from Home Assistant weather entity
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Weather entity ID
        
    Returns:
        dict: Weather forecast data or None on failure
    """
    logger.section("Getting Weather Forecast")
    
    try:
        # Call the get_forecasts service WITH return_response parameter
        url = f"{hass_url}/api/services/weather/get_forecasts?return_response"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "type": "daily",
            "entity_id": entity_id
        }
        
        logger.info(f"Fetching forecast data for {entity_id}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info("Successfully retrieved response data")
            
            # Extract service_response if present
            if "service_response" in response_data:
                forecast_data = response_data["service_response"]
                logger.info("Extracted service_response from data")
            else:
                forecast_data = response_data
            
            # Check if we have valid data
            if (entity_id in forecast_data and 
                "forecast" in forecast_data[entity_id] and 
                forecast_data[entity_id]["forecast"] and 
                len(forecast_data[entity_id]["forecast"]) >= 3):
                
                logger.info(f"Found {len(forecast_data[entity_id]['forecast'])} days of forecast data")
                return forecast_data
            else:
                logger.error("Invalid or insufficient forecast data returned")
                logger.info(f"Available keys in forecast_data: {list(forecast_data.keys())}")
                if entity_id in forecast_data:
                    logger.info(f"Keys in entity data: {list(forecast_data[entity_id].keys())}")
                return None
        else:
            logger.error(f"Error fetching forecast data: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Exception getting weather forecast: {str(e)}")
        return None


def send_temperature_forecast(hass_url, hass_token, forecast_data, entity_id="weather.openweathermap"):
    """
    Process and send a temperature forecast notification
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        forecast_data: Weather forecast data from get_forecast_data()
        entity_id: Weather entity ID
        
    Returns:
        bool: Success status
    """
    if not config_manager.is_enabled('weather.daily_forecast'):
        logger.info("Daily temperature forecast is disabled in configuration")
        return False
    
    try:
        # Extract data for the next 3 days
        forecast = forecast_data[entity_id]["forecast"]
        day_1 = forecast[0]
        day_2 = forecast[1]
        day_3 = forecast[2]
        
        # Extract temperatures
        today_high = round(day_1.get("temperature", 0), 1)
        today_low = round(day_1.get("templow", 0), 1)
        tomorrow_high = round(day_2.get("temperature", 0), 1)
        tomorrow_low = round(day_2.get("templow", 0), 1)
        day_after_tomorrow_high = round(day_3.get("temperature", 0), 1)
        day_after_tomorrow_low = round(day_3.get("templow", 0), 1)
        
        # Format the message
        today_date = datetime.datetime.now().strftime('%Y-%m-%d')
        message = f"{today_date}\n"
        message += "3 Day ❄️ Low Temp Forecast\n"
        message += f"Today: {today_low}°C\n"
        message += f"Tomorrow: {tomorrow_low}°C\n"
        message += f"Day After Tomorrow: {day_after_tomorrow_low}°C"
        
        # Send the notification
        success = send_telegram(message, hass_token)
        
        if success:
            logger.info("Sent temperature forecast notification")
        
        return success
        
    except Exception as e:
        logger.error(f"Error processing temperature forecast: {str(e)}")
        return False


def send_extreme_weather_alert(hass_url, hass_token, forecast_data, entity_id="weather.openweathermap"):
    """
    Check for and notify about extreme weather conditions
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        forecast_data: Weather forecast data from get_forecast_data()
        entity_id: Weather entity ID
        
    Returns:
        bool: Success status
    """
    if not config_manager.is_enabled('weather.extreme_weather_alert'):
        logger.info("Extreme weather alerts are disabled in configuration")
        return False
    
    try:
        # Extract data for the next 3 days
        forecast = forecast_data[entity_id]["forecast"]
        day_1 = forecast[0]
        day_2 = forecast[1]
        day_3 = forecast[2]
        
        # Check for rain
        rain = (
            (day_1.get("precipitation", 0) > 0) or
            (day_2.get("precipitation", 0) > 0) or
            (day_3.get("precipitation", 0) > 0)
        )
        
        # Check for wind
        wind = (
            (day_1.get("wind_speed", 0) > 10) or
            (day_2.get("wind_speed", 0) > 10) or
            (day_3.get("wind_speed", 0) > 10)
        )
        
        # Check for snow
        snow = (
            (day_1.get("condition", "") == "snowy") or
            (day_2.get("condition", "") == "snowy") or
            (day_3.get("condition", "") == "snowy")
        )
        
        # Construct message
        if rain or wind or snow:
            message = ""
            if rain:
                message += "☔ There will be rain in the next 3 days.\n"
            if wind:
                message += "🍃 There will be notable wind in the next 3 days.\n"
            if snow:
                message += "❄️ Snow is expected in the next 3 days.\n"
        else:
            message = "🌤️ Weather is normal."
        
        # Send the notification
        success = send_telegram(message, hass_token)
        
        if success:
            logger.info("Sent extreme weather alert notification")
        
        return success
        
    except Exception as e:
        logger.error(f"Error processing extreme weather alert: {str(e)}")
        return False


def process_weather_data(hass_url, hass_token, entity_id="weather.openweathermap"):
    """
    Main function to process weather data and send notifications
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        entity_id: Weather entity ID
        
    Returns:
        bool: Overall success status
    """
    if not config_manager.is_enabled('weather.enabled'):
        logger.info("Weather features are disabled in configuration")
        return False
    
    logger.section("Processing Weather Data")
    
    try:
        # Get forecast data
        forecast_data = get_forecast_data(hass_url, hass_token, entity_id)
        
        if not forecast_data:
            error_msg = "⚠️ Failed to fetch sufficient daily forecast data from OpenWeatherMap."
            logger.error(error_msg)
            send_telegram(error_msg, hass_token)
            return False
        
        # Process temperature forecast
        temp_success = send_temperature_forecast(hass_url, hass_token, forecast_data, entity_id)
        
        # Process extreme weather alert
        weather_success = send_extreme_weather_alert(hass_url, hass_token, forecast_data, entity_id)
        
        return temp_success and weather_success
        
    except Exception as e:
        error_msg = f"⚠️ Error processing weather data: {str(e)}"
        logger.error(error_msg)
        send_telegram(error_msg, hass_token)
        return False


def main():
    """Main function when run as a script"""
    # Get command line arguments
    if len(sys.argv) < 2:
        error_msg = "⚠️ Not enough arguments. Usage: weather.py <hass_token> [entity_id]"
        logger.error(error_msg)
        print(error_msg)
        return
    
    hass_token = sys.argv[1]
    hass_url = "http://localhost:8123"
    
    # Use custom entity_id if provided
    entity_id = "weather.openweathermap"
    if len(sys.argv) > 2:
        entity_id = sys.argv[2]
    
    # Process weather data
    process_weather_data(hass_url, hass_token, entity_id)


if __name__ == "__main__":
    main()
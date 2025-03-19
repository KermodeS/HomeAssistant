#!/usr/bin/env python3
"""
Grocy integration module for Home Assistant
Fetches chores and sends notifications
"""
import requests
import datetime
import json
import re
import sys
from common import get_logger, send_telegram, config_manager

# Set up logger
logger = get_logger("grocy")


def extract_sections(description):
    """
    Extract sections from description using --- delimiters
    
    Args:
        description: Raw description text with sections
        
    Returns:
        dict: Dictionary with extracted sections
    """
    if not description:
        return {"main": "None", "references": "None", "equipment": "None"}
    
    sections = {"main": "None", "references": "None", "equipment": "None"}
    
    # Log the raw description for debugging
    logger.debug(f"Raw description:\n{description}")
    
    # Split by "---" lines to get the distinct sections
    parts = re.split(r'\n\s*---\s*\n', description)
    logger.debug(f"Split description into {len(parts)} parts")
    
    # First section is the main description (it might have leading ---)
    if len(parts) > 0:
        main_desc = parts[0].strip()
        if main_desc.startswith("---"):
            main_desc = main_desc[3:].strip()
        if main_desc:
            sections["main"] = main_desc
    
    # Extract references section (second part, after "References:" label)
    if len(parts) > 1 and "References:" in parts[1]:
        references_part = parts[1].split("References:", 1)[1].strip()
        sections["references"] = references_part if references_part else "None"
    
    # Extract equipment section (third part, after "Equipment:" label)
    if len(parts) > 2:
        if "Equipment:" in parts[2]:
            equipment_part = parts[2].split("Equipment:", 1)[1].strip()
            sections["equipment"] = equipment_part if equipment_part else "None"
    
    # Debug output for each section
    for section_name, content in sections.items():
        logger.debug(f"Extracted {section_name} section: {content}")
    
    return sections


def get_upcoming_chores(grocy_url, grocy_api_key, days_ahead=14):
    """
    Get upcoming chores from Grocy API
    
    Args:
        grocy_url: Grocy API URL
        grocy_api_key: Grocy API key
        days_ahead: Number of days to look ahead
        
    Returns:
        list: List of upcoming chores with details
    """
    logger.section("Fetching Grocy Chores")
    
    # Remove trailing slash if present
    grocy_url = grocy_url.rstrip('/')
    
    logger.info(f"Using Grocy URL: {grocy_url}")
    
    try:
        # Get the base URL (remove any API path)
        base_parts = grocy_url.split('/')
        if len(base_parts) >= 3:
            # Extract the base URL (protocol + domain + port)
            base_url = '/'.join(base_parts[:3])
        else:
            base_url = grocy_url
            
        logger.info(f"Base URL: {base_url}")
            
        # Try both endpoints
        endpoints = [
            f"{base_url}/api/chores",           # This endpoint gives the chore overview with next execution dates
            f"{base_url}/api/objects/chores"    # This endpoint gives the chore base data
        ]
        
        headers = {
            "GROCY-API-KEY": grocy_api_key,
            "Content-Type": "application/json"
        }
        
        # Store chore details separately
        chore_details = {}
        
        # Get all upcoming chores
        upcoming_chores = []
        
        for endpoint in endpoints:
            logger.info(f"Fetching chores from: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Successfully retrieved data from {endpoint}")
                chores_data = response.json()
                logger.info(f"Found {len(chores_data)} items from {endpoint}")
                
                # Set up dates
                today = datetime.datetime.now().date()
                future_date = today + datetime.timedelta(days=days_ahead)
                
                logger.info(f"Today: {today}, Looking ahead to: {future_date}")
                
                # Process the data differently depending on the endpoint
                if chores_data and isinstance(chores_data, list) and len(chores_data) > 0:
                    if "chore_name" in chores_data[0]:
                        # This is the /api/chores endpoint
                        logger.info("Processing data from /api/chores endpoint")
                        
                        for chore in chores_data:
                            if "next_estimated_execution_time" in chore and chore["next_estimated_execution_time"]:
                                # Extract the date part (remove time)
                                date_str = chore["next_estimated_execution_time"]
                                # Handle different date formats
                                if "T" in date_str:
                                    chore_date_str = date_str.split("T")[0]
                                else:
                                    chore_date_str = date_str.split(" ")[0]
                                    
                                try:
                                    chore_date = datetime.datetime.strptime(chore_date_str, "%Y-%m-%d").date()
                                    
                                    logger.debug(f"Chore: {chore.get('chore_name', 'Unknown')}, Due: {chore_date}")
                                    
                                    # Check if chore is within our date range
                                    if today <= chore_date <= future_date:
                                        logger.info(f"Found upcoming chore: {chore.get('chore_name', 'Unknown')}")
                                        
                                        # Format due date to be more readable
                                        due_date = chore_date.strftime("%A, %b %d")
                                        
                                        # Extract assigned user
                                        assigned_to = chore.get("next_execution_assigned_user", {})
                                        assigned_name = assigned_to.get("display_name", "Unassigned") if isinstance(assigned_to, dict) else "Unassigned"
                                        
                                        # Add to upcoming chores list
                                        upcoming_chores.append({
                                            "name": chore.get("chore_name", "Unknown chore"),
                                            "date": due_date,
                                            "assigned_to": assigned_name,
                                            "description": "",  # We'll get this from objects/chores if needed
                                            "userfields": None,  # We'll get this from objects/chores if needed
                                            "sections": {}      # We'll extract sections from the description
                                        })
                                except Exception as e:
                                    logger.error(f"Error processing chore date for {chore.get('chore_name', 'Unknown')}: {str(e)}")
                    
                    elif "name" in chores_data[0]:
                        # This is the /api/objects/chores endpoint
                        logger.info("Processing data from /api/objects/chores endpoint")
                        
                        # Store all chore details for future reference
                        for chore in chores_data:
                            chore_name = chore.get("name", "")
                            description = chore.get("description", "")
                            
                            # Extract sections from description
                            sections = extract_sections(description)
                            
                            chore_details[chore_name] = {
                                "full_description": description,
                                "userfields": chore.get("userfields", None),
                                "sections": sections
                            }
                            
                            # Log the userfields for debugging
                            logger.debug(f"Chore {chore_name} userfields: {chore.get('userfields')}")
                            
                            # We also use this to add details to chores we already found
                            for upcoming in upcoming_chores:
                                if upcoming["name"] == chore_name:
                                    # For the message, use only the main section
                                    main_desc = sections.get("main", "None")
                                    upcoming["description"] = main_desc
                                    upcoming["userfields"] = chore.get("userfields")
                                    upcoming["sections"] = sections
                                    logger.debug(f"Added details for chore {upcoming['name']}")
        
        # Add details for chores if we didn't get them yet
        if upcoming_chores:
            for chore in upcoming_chores:
                if (chore["description"] == "" or chore["userfields"] is None or not chore["sections"]) and chore["name"] in chore_details:
                    details = chore_details[chore["name"]]
                    
                    if chore["description"] == "" and details["sections"].get("main"):
                        chore["description"] = details["sections"].get("main", "None")
                    
                    if chore["userfields"] is None and "userfields" in details:
                        chore["userfields"] = details["userfields"]
                        
                    if not chore["sections"] and "sections" in details:
                        chore["sections"] = details["sections"]
                        
                    logger.debug(f"Added cached details for {chore['name']}")
                    
        logger.info(f"Found {len(upcoming_chores)} upcoming chores in the next {days_ahead} days")
        return upcoming_chores
        
    except Exception as e:
        logger.error(f"Error fetching chores: {str(e)}")
        return []


def format_chores_message(chores):
    """
    Format the chores list into a notification message
    
    Args:
        chores: List of chore dictionaries
        
    Returns:
        str: Formatted message
    """
    if not chores:
        return "✅ No chores scheduled for the next 14 days."
    
    message = "📋 Upcoming chores for the next 14 days:\n\n"
    
    for chore in chores:
        message += f"*Data:* {chore['date']}\n"
        message += f"*Chore name:* {chore['name']}\n"
        message += f"*Assigned to:* {chore['assigned_to']}\n"
        
        # Add location from userfields if available
        if chore["userfields"]:
            try:
                # Try to parse as JSON if it's a string
                userfields_data = chore["userfields"]
                if isinstance(userfields_data, str) and userfields_data.strip():
                    try:
                        userfields_data = json.loads(userfields_data)
                    except:
                        # If it's not valid JSON, just use as is
                        pass
                
                # Extract location field specifically
                if isinstance(userfields_data, dict):
                    # Look for any field that might represent location
                    location_keys = ["Luogo_di_lavoro", "Luogodilavoro", "location", "Location"]
                    location = None
                    
                    for key in location_keys:
                        if key in userfields_data and userfields_data[key]:
                            location = userfields_data[key]
                            break
                    
                    if location:
                        message += f"*Luogo di lavoro:* {location}\n"
            except Exception as e:
                logger.error(f"Error processing userfields: {str(e)}")
        
        # Add main description
        if chore['description']:
            message += f"*Description:* {chore['description']}\n"
        
        # Add references section if available and not "None"
        references = chore["sections"].get("references", "None")
        if references and references != "None":
            message += f"*References:* {references}\n"
        else:
            message += "*References:* None\n"
        
        # Add equipment section if available and not "None"
        equipment = chore["sections"].get("equipment", "None")
        if equipment and equipment != "None":
            message += f"*Equipment:*\n{equipment}\n"
        else:
            message += "*Equipment:* None\n"
        
        message += "\n"
    
    return message


def notify_chores(grocy_url, grocy_api_key, hass_token, hass_url="http://localhost:8123", days_ahead=14):
    """
    Main function to fetch chores and send notifications
    
    Args:
        grocy_url: Grocy API URL
        grocy_api_key: Grocy API key
        hass_token: Home Assistant long-lived access token
        hass_url: Home Assistant URL
        days_ahead: Number of days to look ahead
        
    Returns:
        bool: Success status
    """
    if not config_manager.is_enabled('grocy.chores_notification'):
        logger.info("Grocy chores notifications are disabled in configuration")
        return False
    
    logger.section("Grocy Chores Notification")
    
    try:
        # Get upcoming chores
        chores = get_upcoming_chores(grocy_url, grocy_api_key, days_ahead)
        
        # Format the message
        message = format_chores_message(chores)
        
        # Send the notification
        success = send_telegram(message, hass_token, markdown=True)
        
        if success:
            logger.info(f"Sent notification with {len(chores)} chores")
        else:
            logger.error("Failed to send notification")
        
        return success
        
    except Exception as e:
        error_msg = f"⚠️ Error checking chores: {str(e)}"
        logger.error(error_msg)
        try:
            send_telegram(error_msg, hass_token)
        except:
            logger.error("Failed to send error notification")
        return False


def main():
    """Main function when run as a script"""
    # Get command line arguments
    if len(sys.argv) < 4:
        error_msg = "⚠️ Not enough arguments. Usage: grocy.py <grocy_url> <grocy_api_key> <hass_token>"
        logger.error(error_msg)
        print(error_msg)
        return
    
    grocy_url = sys.argv[1]
    grocy_api_key = sys.argv[2]
    hass_token = sys.argv[3]
    
    # Run the notification
    notify_chores(grocy_url, grocy_api_key, hass_token)


if __name__ == "__main__":
    main()
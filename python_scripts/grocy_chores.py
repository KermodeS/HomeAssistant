#!/usr/bin/env python3
"""
Grocy chores script that fetches upcoming chores and sends notifications
with bold section titles and fixed equipment parsing
"""
import requests
import datetime
import sys
import json
import re

# Set up basic debugging
DEBUG = True

def log_debug(message):
    """Debug logging function"""
    if DEBUG:
        try:
            with open("/config/www/grocy_debug.log", "a") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{timestamp}: {message}\n")
            print(message)  # Also print to stdout
        except Exception as e:
            print(f"Error writing to debug log: {str(e)}")

def send_notification(message, hass_url="http://localhost:8123", hass_token=None):
    """Send telegram notification via Home Assistant API"""
    if not hass_token:
        log_debug("Error: HASS_TOKEN not provided")
        return False
    
    try:
        # Use the notify service with markdown formatting
        url = f"{hass_url}/api/services/notify/kermode"
        headers = {
            "Authorization": f"Bearer {hass_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "message": message,
            "data": {
                "parse_mode": "markdown"  # Enable markdown for bold text
            }
        }
        
        log_debug(f"Sending notification to {url}")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            log_debug("Notification sent successfully")
            return True
        else:
            log_debug(f"Error sending notification: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        log_debug(f"Exception sending notification: {str(e)}")
        return False

def extract_sections(description):
    """Extract sections from description using --- delimiters"""
    if not description:
        return {"main": "None", "references": "None", "equipment": "None"}
    
    sections = {"main": "None", "references": "None", "equipment": "None"}
    
    # Log the raw description for debugging
    log_debug(f"Raw description:\n{description}")
    
    # Split by "---" lines to get the distinct sections
    parts = re.split(r'\n\s*---\s*\n', description)
    log_debug(f"Split description into {len(parts)} parts")
    
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
        log_debug(f"Extracted {section_name} section: {content}")
    
    return sections

def main():
    """Main function to fetch chores and send notifications"""
    log_debug("\n\n----------")
    log_debug("Starting Grocy chores script")
    
    # Get command line arguments
    if len(sys.argv) < 4:
        error_msg = "⚠️ Not enough arguments. Usage: script.py <grocy_url> <grocy_api_key> <hass_token>"
        log_debug(error_msg)
        print(error_msg)
        return
    
    grocy_url = sys.argv[1].rstrip('/')  # Remove trailing slash if present
    grocy_api_key = sys.argv[2]
    hass_token = sys.argv[3]
    hass_url = "http://localhost:8123"  # Define hass_url for HA API calls
    
    log_debug(f"Using Grocy URL: {grocy_url}")
    
    try:
        # Get the base URL (remove any API path)
        base_parts = grocy_url.split('/')
        if len(base_parts) >= 3:
            # Extract the base URL (protocol + domain + port)
            base_url = '/'.join(base_parts[:3])
        else:
            base_url = grocy_url
            
        log_debug(f"Base URL: {base_url}")
            
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
            log_debug(f"Fetching chores from: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                log_debug(f"Successfully retrieved data from {endpoint}")
                chores_data = response.json()
                log_debug(f"Found {len(chores_data)} items from {endpoint}")
                
                # Set up dates
                today = datetime.datetime.now().date()
                future_date = today + datetime.timedelta(days=14)
                
                log_debug(f"Today: {today}, Looking ahead to: {future_date}")
                
                # Process the data differently depending on the endpoint
                if chores_data and isinstance(chores_data, list) and len(chores_data) > 0:
                    if "chore_name" in chores_data[0]:
                        # This is the /api/chores endpoint
                        log_debug("Processing data from /api/chores endpoint")
                        
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
                                    
                                    log_debug(f"Chore: {chore.get('chore_name', 'Unknown')}, Due: {chore_date}")
                                    
                                    # Check if chore is within our date range (next 14 days)
                                    if today <= chore_date <= future_date:
                                        log_debug(f"Found upcoming chore: {chore.get('chore_name', 'Unknown')}")
                                        
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
                                    log_debug(f"Error processing chore date for {chore.get('chore_name', 'Unknown')}: {str(e)}")
                    
                    elif "name" in chores_data[0]:
                        # This is the /api/objects/chores endpoint
                        log_debug("Processing data from /api/objects/chores endpoint")
                        
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
                            log_debug(f"Chore {chore_name} userfields: {chore.get('userfields')}")
                            
                            # We also use this to add details to chores we already found
                            for upcoming in upcoming_chores:
                                if upcoming["name"] == chore_name:
                                    # For the message, use only the main section
                                    main_desc = sections.get("main", "None")
                                    upcoming["description"] = main_desc
                                    upcoming["userfields"] = chore.get("userfields")
                                    upcoming["sections"] = sections
                                    log_debug(f"Added details for chore {upcoming['name']}")
        
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
                        
                    log_debug(f"Added cached details for {chore['name']}")
        
        # Send notification
        log_debug(f"Found {len(upcoming_chores)} upcoming chores in the next 14 days")
        if upcoming_chores:
            message = "📋 Upcoming chores for the next 14 days:\n\n"
            for chore in upcoming_chores:
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
                        log_debug(f"Error processing userfields: {str(e)}")
                
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
                
            send_notification(message, hass_url=hass_url, hass_token=hass_token)
            log_debug(f"Sent notification with {len(upcoming_chores)} chores")
        else:
            message = "✅ No chores scheduled for the next 14 days."
            send_notification(message, hass_url=hass_url, hass_token=hass_token)
            log_debug("No upcoming chores found")
                
    except Exception as e:
        error_msg = f"⚠️ Error checking chores: {str(e)}"
        log_debug(error_msg)
        send_notification(error_msg, hass_url=hass_url, hass_token=hass_token)

if __name__ == "__main__":
    main()
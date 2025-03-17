#!/usr/bin/env python3
"""
Grocy dashboard data provider for Home Assistant
Creates a JSON file with chores data for the custom card
"""
import requests
import json
import os
from datetime import datetime
from common import get_logger, config_manager

# Set up logger
logger = get_logger("grocy_dashboard")

def format_chores_for_dashboard(chores):
    """Format chores data for the dashboard"""
    formatted_chores = []
    
    for chore in chores:
        # Determine the due status
        due_date = chore.get('date', '')
        today = datetime.now().strftime("%A, %b %d")
        
        # Determine due status based on the date
        if due_date == today:
            due_status = 'today'
        elif 'overdue' in due_date.lower():
            due_status = 'overdue'
        elif 'tomorrow' in due_date.lower():
            due_status = 'tomorrow'
        else:
            due_status = 'upcoming'
            
        # Extract territorio and luogo_di_lavoro from userfields
        userfields = chore.get('userfields', {})
        territorio = "Unspecified"
        luogo_di_lavoro = "Unspecified"
        
        if userfields:
            try:
                # Parse userfields if it's a string
                if isinstance(userfields, str) and userfields.strip():
                    try:
                        userfields = json.loads(userfields)
                    except:
                        pass
                
                # Check for location fields
                if isinstance(userfields, dict):
                    # Look for territorio fields
                    for key in ["Territorio", "territorio", "Territory"]:
                        if key in userfields and userfields[key]:
                            territorio = userfields[key]
                            break
                    
                    # Look for location fields
                    for key in ["Luogo_di_lavoro", "Luogodilavoro", "location", "Location"]:
                        if key in userfields and userfields[key]:
                            luogo_di_lavoro = userfields[key]
                            break
            except Exception as e:
                logger.error(f"Error processing userfields: {str(e)}")
        
        # Create the formatted chore entry
        formatted_chore = {
            "name": chore.get('name', 'Unknown'),
            "date": due_date,
            "dueStatus": due_status,
            "assigned_to": chore.get('assigned_to', 'Unassigned'),
            "description": chore.get('description', ''),
            "territorio": territorio,
            "luogo_di_lavoro": luogo_di_lavoro
        }
        
        # Add sections if available
        sections = chore.get('sections', {})
        if sections:
            formatted_chore["references"] = sections.get('references', 'None')
            formatted_chore["equipment"] = sections.get('equipment', 'None')
        else:
            formatted_chore["references"] = "None"
            formatted_chore["equipment"] = "None"
        
        formatted_chores.append(formatted_chore)
    
    logger.info(f"Formatted {len(formatted_chores)} chores for dashboard")
    return formatted_chores

def save_dashboard_data(chores, file_path='/config/www/grocy_dashboard_data.json'):
    """Save formatted chores data to a JSON file for the dashboard"""
    try:
        # Format the chores data
        dashboard_data = format_chores_for_dashboard(chores)
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        logger.info(f"Saved dashboard data with {len(chores)} chores to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving dashboard data: {str(e)}")
        return False

def update_dashboard_data(grocy_url, grocy_api_key, days_ahead=14):
    """Update the dashboard data file with the latest chores"""
    logger.section("Updating Grocy Dashboard Data")
    
    try:
        # Import here to avoid circular imports
        from services.grocy import get_upcoming_chores
        
        # Get upcoming chores using your existing function
        logger.info(f"Getting chores from Grocy URL: {grocy_url}")
        chores = get_upcoming_chores(grocy_url, grocy_api_key, days_ahead)
        
        if not chores:
            logger.warning("No chores found, dashboard will be empty")
            # Save empty array if no chores
            with open('/config/www/grocy_dashboard_data.json', 'w') as f:
                json.dump([], f)
            return True
        
        logger.info(f"Retrieved {len(chores)} chores from Grocy")
        
        # Save the data for the dashboard
        success = save_dashboard_data(chores)
        
        return success
    except Exception as e:
        logger.error(f"Error updating dashboard data: {str(e)}")
        logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
        return False
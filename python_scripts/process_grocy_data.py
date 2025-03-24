# Create script at /config/python_scripts/process_grocy_data.py
#!/usr/bin/env python3
"""
Script to process Grocy dashboard data into individual chore files
"""
import json
import os
import sys

def process_data():
    """Process grocy data file into multiple smaller files"""
    try:
        # Define paths
        input_path = "/config/www/grocy_dashboard_data.json"
        output_dir = "/config/www/grocy_processed"
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Read input data
        if not os.path.exists(input_path):
            print(f"Input file not found: {input_path}")
            return False
            
        with open(input_path, 'r') as f:
            data = json.load(f)
        
        if not data:
            print("No data found in JSON file")
            return False
            
        # Write summary file
        territories = []
        locations = []
        people = []
        
        for item in data:
            if "territorio" in item and item["territorio"]:
                territories.append(item["territorio"])
            if "luogo_di_lavoro" in item and item["luogo_di_lavoro"]:
                locations.append(item["luogo_di_lavoro"])
            if "assigned_to" in item and item["assigned_to"]:
                people.append(item["assigned_to"])
        
        summary = {
            "count": len(data),
            "has_data": len(data) > 0,
            "territories": list(set(territories)),
            "locations": list(set(locations)),
            "people": list(set(people))
        }
        
        with open(f"{output_dir}/summary.json", 'w') as f:
            json.dump(summary, f)
            
        # Write individual chore files
        for i, chore in enumerate(data):
            with open(f"{output_dir}/chore_{i}.json", 'w') as f:
                json.dump(chore, f)
                
        # Create index file with IDs
        index = {str(i): chore.get("name", f"Chore {i}") for i, chore in enumerate(data)}
        with open(f"{output_dir}/index.json", 'w') as f:
            json.dump(index, f)
            
        print(f"Processed {len(data)} chores successfully")
        return True
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return False

if __name__ == "__main__":
    process_data()
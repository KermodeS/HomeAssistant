# Debug script to check if JSON file exists and has data
import json
import os

def check_dashboard_data():
    file_path = '/config/www/grocy_dashboard_data.json'
    
    if not os.path.exists(file_path):
        print(f"ERROR: Dashboard data file does not exist at {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        print(f"SUCCESS: Dashboard data file exists with {len(data)} chores")
        print(f"Sample data: {data[0] if data else 'No data'}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to read dashboard data file: {str(e)}")
        return False

if __name__ == "__main__":
    check_dashboard_data()
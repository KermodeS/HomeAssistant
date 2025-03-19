#!/usr/bin/env python3
"""
Storage management service for Home Assistant
Handles log file rotation and disk usage monitoring
"""
import os
import glob
import datetime
import shutil
import sys
import json
from common import get_logger, send_telegram, config_manager

# Set up logger
logger = get_logger("storage")

def get_directory_size(path):
    """
    Get the size of a directory and all its contents in bytes
    
    Args:
        path: Directory path
        
    Returns:
        int: Size in bytes
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):  # Skip symbolic links
                try:
                    total_size += os.path.getsize(fp)
                except OSError:
                    logger.error(f"Could not get size of {fp}")
    return total_size

def get_log_files_info(log_dir="/config/www/logs"):
    """
    Get information about log files
    
    Args:
        log_dir: Directory containing log files
        
    Returns:
        dict: Dictionary with log files information
    """
    logger.section("Getting Log Files Information")
    
    try:
        # Check if the directory exists
        if not os.path.exists(log_dir):
            logger.error(f"Log directory {log_dir} does not exist")
            return {"error": f"Log directory {log_dir} does not exist"}
        
        # Get all .log files
        log_files = glob.glob(os.path.join(log_dir, "*.log"))
        logger.info(f"Found {len(log_files)} log files")
        
        # Get total size
        total_size = sum(os.path.getsize(f) for f in log_files)
        logger.info(f"Total log size: {total_size / 1024 / 1024:.2f} MB")
        
        # Get info for each file
        files_info = []
        for log_file in log_files:
            file_name = os.path.basename(log_file)
            file_size = os.path.getsize(log_file)
            file_mtime = os.path.getmtime(log_file)
            file_date = datetime.datetime.fromtimestamp(file_mtime)
            
            files_info.append({
                "name": file_name,
                "size": file_size,
                "size_human": f"{file_size / 1024:.2f} KB",
                "last_modified": file_date.strftime("%Y-%m-%d %H:%M:%S"),
                "days_old": (datetime.datetime.now() - file_date).days
            })
        
        # Sort by size (largest first)
        files_info.sort(key=lambda x: x["size"], reverse=True)
        
        return {
            "total_size": total_size,
            "total_size_human": f"{total_size / 1024 / 1024:.2f} MB",
            "file_count": len(log_files),
            "files": files_info
        }
        
    except Exception as e:
        logger.error(f"Error getting log files info: {str(e)}")
        return {"error": str(e)}

def rotate_log_files(max_size_kb=1024, max_age_days=30, log_dir="/config/www/logs"):
    """
    Rotate log files based on size and age
    
    Args:
        max_size_kb: Maximum file size in KB
        max_age_days: Maximum file age in days
        log_dir: Directory containing log files
        
    Returns:
        dict: Summary of rotated files
    """
    logger.section("Rotating Log Files")
    
    try:
        # Convert max_size to bytes
        max_size = max_size_kb * 1024
        
        # Get current date
        now = datetime.datetime.now()
        
        # Track rotated files
        rotated_files = []
        total_reclaimed = 0
        
        # Check if the directory exists
        if not os.path.exists(log_dir):
            logger.error(f"Log directory {log_dir} does not exist")
            return {"error": f"Log directory {log_dir} does not exist"}
        
        # Get all .log files
        log_files = glob.glob(os.path.join(log_dir, "*.log"))
        logger.info(f"Found {len(log_files)} log files to check")
        
        # Archive directory
        archive_dir = os.path.join(log_dir, "archive")
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
        
        # Process each file
        for log_file in log_files:
            file_name = os.path.basename(log_file)
            file_size = os.path.getsize(log_file)
            file_mtime = os.path.getmtime(log_file)
            file_date = datetime.datetime.fromtimestamp(file_mtime)
            file_age = (now - file_date).days
            
            # Skip archive directory
            if log_file.startswith(archive_dir):
                continue
            
            # Check if file exceeds size or age limits
            if file_size > max_size or file_age > max_age_days:
                # Skip rotation if file was modified in the last hour (active file)
                if (now - file_date).seconds < 300:
                    logger.info(f"Skipping active file: {file_name}")
                    continue
                
                # Generate archive name with timestamp
                timestamp = file_date.strftime("%Y%m%d")
                archive_name = f"{os.path.splitext(file_name)[0]}_{timestamp}.log"
                archive_path = os.path.join(archive_dir, archive_name)
                
                # Check if archived file already exists
                if os.path.exists(archive_path):
                    logger.info(f"Archive already exists for {file_name}, truncating instead")
                    # Truncate the file instead of moving
                    with open(log_file, 'w') as f:
                        f.write(f"Log rotated at {now} due to ")
                        if file_size > max_size:
                            f.write(f"size ({file_size / 1024:.2f} KB > {max_size / 1024:.2f} KB)\n")
                        else:
                            f.write(f"age ({file_age} days > {max_age_days} days)\n")
                else:
                    # Move the file to archive
                    logger.info(f"Moving {file_name} to archive")
                    shutil.move(log_file, archive_path)
                    
                    # Create empty file with header
                    with open(log_file, 'w') as f:
                        f.write(f"Log rotated at {now}\n")
                
                rotated_files.append({
                    "name": file_name,
                    "size": file_size,
                    "size_human": f"{file_size / 1024:.2f} KB",
                    "age": file_age,
                    "reason": "size" if file_size > max_size else "age"
                })
                
                total_reclaimed += file_size
        
        # Clean up old archives (> 90 days)
        archive_files = glob.glob(os.path.join(archive_dir, "*.log"))
        for archive_file in archive_files:
            file_mtime = os.path.getmtime(archive_file)
            file_date = datetime.datetime.fromtimestamp(file_mtime)
            file_age = (now - file_date).days
            
            if file_age > 90:
                logger.info(f"Removing old archive: {os.path.basename(archive_file)}")
                os.remove(archive_file)
                rotated_files.append({
                    "name": os.path.basename(archive_file),
                    "action": "deleted"
                })
        
        return {
            "rotated_count": len(rotated_files),
            "reclaimed_space": total_reclaimed,
            "reclaimed_space_human": f"{total_reclaimed / 1024 / 1024:.2f} MB",
            "rotated_files": rotated_files
        }
        
    except Exception as e:
        logger.error(f"Error rotating log files: {str(e)}")
        return {"error": str(e)}

def check_disk_space():
    """
    Check available disk space
    
    Returns:
        dict: Disk space information
    """
    logger.section("Checking Disk Space")
    
    try:
        # Get disk usage for /config
        stat = shutil.disk_usage("/config")
        total = stat.total
        used = stat.used
        free = stat.free
        
        # Calculate percentage
        used_percent = (used / total) * 100
        
        logger.info(f"Total disk space: {total / (1024**3):.2f} GB")
        logger.info(f"Used disk space: {used / (1024**3):.2f} GB ({used_percent:.1f}%)")
        logger.info(f"Free disk space: {free / (1024**3):.2f} GB")
        
        return {
            "total": total,
            "total_human": f"{total / (1024**3):.2f} GB",
            "used": used,
            "used_human": f"{used / (1024**3):.2f} GB",
            "used_percent": f"{used_percent:.1f}%",
            "free": free,
            "free_human": f"{free / (1024**3):.2f} GB"
        }
        
    except Exception as e:
        logger.error(f"Error checking disk space: {str(e)}")
        return {"error": str(e)}

def export_storage_data(data, hass_url):
    """
    Export storage data to JSON for dashboard consumption
    
    Args:
        data: Storage data to export
        hass_url: Home Assistant URL (not used, included for consistency)
        
    Returns:
        bool: Success status
    """
    try:
        # Create directory if it doesn't exist
        data_dir = "/config/www/data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Write data to JSON file
        data_file = os.path.join(data_dir, "storage_data.json")
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Storage data exported to {data_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting storage data: {str(e)}")
        return False

def send_disk_alert(disk_data, hass_token, threshold=90):
    """
    Send alert if disk usage exceeds threshold
    
    Args:
        disk_data: Disk space information
        hass_token: Home Assistant long-lived access token
        threshold: Disk usage threshold in percent
        
    Returns:
        bool: Whether alert was sent
    """
    try:
        # Check if disk usage exceeds threshold
        used_percent = (disk_data["used"] / disk_data["total"]) * 100
        
        if used_percent > threshold:
            message = (
                f"⚠️ *Disk Space Alert*\n\n"
                f"Disk usage has reached {used_percent:.1f}%, which exceeds the {threshold}% threshold.\n\n"
                f"Total: {disk_data['total_human']}\n"
                f"Used: {disk_data['used_human']}\n"
                f"Free: {disk_data['free_human']}\n\n"
                f"Please free up disk space to prevent issues."
            )
            
            logger.warning(f"Disk usage alert: {used_percent:.1f}% > {threshold}%")
            
            # Send alert
            send_telegram(message, hass_token, markdown=True)
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error sending disk alert: {str(e)}")
        return False

def manage_storage(hass_url, hass_token, max_log_size=1024, max_log_age=30):
    """
    Main function to manage storage
    
    Args:
        hass_url: Home Assistant URL
        hass_token: Home Assistant long-lived access token
        max_log_size: Maximum log file size in KB
        max_log_age: Maximum log file age in days
        
    Returns:
        bool: Overall success status
    """
    if not config_manager.is_enabled('storage.enabled'):
        logger.info("Storage management is disabled in configuration")
        return False
    
    logger.section("Managing Storage")
    
    try:
        # Collect all data
        log_data = get_log_files_info()
        disk_data = check_disk_space()
        
        # Rotate logs if needed
        if config_manager.is_enabled('storage.auto_rotate_logs'):
            rotation_data = rotate_log_files(max_log_size, max_log_age)
        else:
            rotation_data = {"rotated_count": 0, "rotated_files": [], "auto_rotate": "disabled"}
        
        # Combine all data
        storage_data = {
            "logs": log_data,
            "disk": disk_data,
            "rotation": rotation_data,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Export data for dashboard
        export_success = export_storage_data(storage_data, hass_url)
        
        # Send alert if disk usage is high
        if config_manager.is_enabled('storage.disk_alerts'):
            threshold = config_manager.get_config_value('storage.disk_alert_threshold', 90)
            alert_sent = send_disk_alert(disk_data, hass_token, threshold)
            if alert_sent:
                logger.info(f"Disk usage alert sent (threshold: {threshold}%)")
        
        return export_success
        
    except Exception as e:
        error_msg = f"⚠️ Error managing storage: {str(e)}"
        logger.error(error_msg)
        try:
            send_telegram(error_msg, hass_token)
        except:
            logger.error("Failed to send error notification")
        return False

def main():
    """Main function when run as a script"""
    # Get command line arguments
    if len(sys.argv) < 2:
        error_msg = "⚠️ Not enough arguments. Usage: storage.py <hass_token> [max_log_size_kb] [max_log_age_days]"
        logger.error(error_msg)
        print(error_msg)
        return
    
    hass_token = sys.argv[1]
    hass_url = "http://localhost:8123"
    
    # Get optional parameters
    max_log_size = 1024  # 1MB default
    if len(sys.argv) > 2:
        try:
            max_log_size = int(sys.argv[2])
        except ValueError:
            logger.warning(f"Invalid max_log_size: {sys.argv[2]}, using default")
    
    max_log_age = 30  # 30 days default
    if len(sys.argv) > 3:
        try:
            max_log_age = int(sys.argv[3])
        except ValueError:
            logger.warning(f"Invalid max_log_age: {sys.argv[3]}, using default")
    
    # Run storage management
    manage_storage(hass_url, hass_token, max_log_size, max_log_age)

if __name__ == "__main__":
    main()
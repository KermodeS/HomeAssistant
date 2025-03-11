#!/usr/bin/env python3
"""
Log management utility for Home Assistant automation scripts
Handles log rotation, cleanup, and summary generation
"""
import os
import sys
import datetime
import glob
import shutil

LOG_DIR = "/config/www/logs"
MAX_LOG_SIZE = 100 * 1024  # 100KB max log size
MAX_LOG_AGE = 14  # Keep logs for 14 days max
MAX_OLD_LOGS = 5  # Keep at most 5 old versions of each log


def rotate_large_logs():
    """Rotate logs that exceed the maximum size"""
    log_files = glob.glob(f"{LOG_DIR}/*.log")
    rotated_count = 0
    
    for log_file in log_files:
        # Skip already rotated logs
        if ".old" in log_file or ".1" in log_file:
            continue
            
        try:
            # Check file size
            size = os.path.getsize(log_file)
            if size > MAX_LOG_SIZE:
                # Find next available number for rotation
                base_name = log_file
                i = 1
                while os.path.exists(f"{base_name}.{i}") and i < MAX_OLD_LOGS:
                    i += 1
                    
                if i >= MAX_OLD_LOGS:
                    # Remove oldest log if we've reached the limit
                    if os.path.exists(f"{base_name}.{MAX_OLD_LOGS}"):
                        os.remove(f"{base_name}.{MAX_OLD_LOGS}")
                    
                    # Shift all logs down
                    for j in range(MAX_OLD_LOGS-1, 0, -1):
                        if os.path.exists(f"{base_name}.{j}"):
                            os.rename(f"{base_name}.{j}", f"{base_name}.{j+1}")
                    
                    i = 1
                
                # Create the rotated log
                shutil.copy2(log_file, f"{log_file}.{i}")
                
                # Truncate the original log, but keep the header
                with open(log_file, 'w') as f:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"Log rotated at {timestamp}. Previous content in {log_file}.{i}\n")
                
                rotated_count += 1
                print(f"Rotated {log_file} to {log_file}.{i}")
        except Exception as e:
            print(f"Error rotating {log_file}: {str(e)}")
    
    return rotated_count


def cleanup_old_logs():
    """Delete logs older than the maximum age"""
    log_files = glob.glob(f"{LOG_DIR}/*.log*")
    deleted_count = 0
    
    # Get current time
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=MAX_LOG_AGE)
    
    for log_file in log_files:
        try:
            # Get last modified time
            mtime = os.path.getmtime(log_file)
            mtime_dt = datetime.datetime.fromtimestamp(mtime)
            
            if mtime_dt < cutoff:
                os.remove(log_file)
                deleted_count += 1
                print(f"Deleted old log {log_file} (last modified: {mtime_dt.strftime('%Y-%m-%d')})")
        except Exception as e:
            print(f"Error cleaning up {log_file}: {str(e)}")
    
    return deleted_count


def create_log_summary():
    """Create a summary of all logs"""
    log_files = glob.glob(f"{LOG_DIR}/*.log")
    summary_file = f"{LOG_DIR}/summary.log"
    
    try:
        with open(summary_file, 'w') as summary:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            summary.write(f"Log Summary Generated at {timestamp}\n")
            summary.write("=" * 50 + "\n\n")
            
            # List all log files with size and last modified time
            summary.write("Available Log Files:\n")
            for log_file in sorted(log_files):
                name = os.path.basename(log_file)
                size = os.path.getsize(log_file)
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(log_file))
                
                summary.write(f"{name}: {size/1024:.1f}KB, Last modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            summary.write("\n" + "=" * 50 + "\n\n")
            
            # Get the last few lines of each main log file
            main_logs = ["grocy.log", "weather.log", "devices.log", "main.log", "wrapper.log"]
            for log_name in main_logs:
                log_path = f"{LOG_DIR}/{log_name}"
                if os.path.exists(log_path):
                    summary.write(f"Last 10 lines of {log_name}:\n")
                    
                    with open(log_path, 'r') as f:
                        lines = f.readlines()
                        last_lines = lines[-10:] if len(lines) >= 10 else lines
                        for line in last_lines:
                            summary.write(line)
                    
                    summary.write("\n" + "-" * 30 + "\n\n")
        
        print(f"Created log summary at {summary_file}")
        return True
    except Exception as e:
        print(f"Error creating log summary: {str(e)}")
        return False


def main():
    """Main function"""
    print(f"=== Log Manager Started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print(f"Created log directory: {LOG_DIR}")
    
    # Process according to command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "rotate":
            rotated = rotate_large_logs()
            print(f"Rotated {rotated} log files")
        elif command == "cleanup":
            deleted = cleanup_old_logs()
            print(f"Deleted {deleted} old log files")
        elif command == "summary":
            create_log_summary()
        else:
            print("Unknown command. Use: rotate, cleanup, or summary")
    else:
        # Default: do all maintenance tasks
        rotate_large_logs()
        cleanup_old_logs()
        create_log_summary()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Log management utilities for Home Assistant automation
Provides log rotation and cleanup functionality
"""
import os
import glob
import datetime
import shutil
import gzip
from .logger import get_logger
from .config_manager import config_manager

# Set up logger
logger = get_logger("log_manager")


class LogManager:
    """Manages log rotation and cleanup for the automation system"""
    
    def __init__(self, log_dir="/config/www/logs", 
                 max_log_size_kb=1024,
                 max_log_age_days=30,
                 max_logs_per_module=10,
                 compress_rotated=True):
        """
        Initialize the log manager
        
        Args:
            log_dir: Directory where logs are stored
            max_log_size_kb: Maximum size in KB before rotating a log
            max_log_age_days: Maximum age in days before deleting a log
            max_logs_per_module: Maximum number of rotated logs to keep per module
            compress_rotated: Whether to compress rotated logs
        """
        self.log_dir = log_dir
        self.max_log_size_kb = max_log_size_kb
        self.max_log_age_days = max_log_age_days
        self.max_logs_per_module = max_logs_per_module
        self.compress_rotated = compress_rotated
        
        # Ensure log directory exists
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
                logger.info(f"Created log directory: {log_dir}")
            except Exception as e:
                logger.error(f"Failed to create log directory: {str(e)}")
    
    def rotate_logs(self):
        """
        Check all logs and rotate them if they exceed size limit
        
        Returns:
            int: Number of logs rotated
        """
        if not os.path.exists(self.log_dir):
            logger.error(f"Log directory does not exist: {self.log_dir}")
            return 0
        
        logger.info("Starting log rotation check")
        rotated_count = 0
        
        # Get all .log files in the log directory
        log_files = glob.glob(os.path.join(self.log_dir, "*.log"))
        
        for log_path in log_files:
            try:
                # Skip already rotated logs (those with timestamps)
                if "_20" in os.path.basename(log_path):
                    continue
                
                # Check log size
                size_kb = os.path.getsize(log_path) / 1024
                
                if size_kb > self.max_log_size_kb:
                    self._rotate_log(log_path)
                    rotated_count += 1
                    
            except Exception as e:
                logger.error(f"Error checking log {log_path}: {str(e)}")
        
        logger.info(f"Log rotation complete: {rotated_count} logs rotated")
        return rotated_count
    
    def _rotate_log(self, log_path):
        """
        Rotate a specific log file
        
        Args:
            log_path: Path to the log file to rotate
        
        Returns:
            bool: Success status
        """
        try:
            # Get base filename and directory
            log_dir = os.path.dirname(log_path)
            base_name = os.path.basename(log_path)
            
            # Generate timestamp for the rotated log
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create rotated filename
            if "." in base_name:
                name_part, ext_part = base_name.rsplit(".", 1)
                rotated_name = f"{name_part}_{timestamp}.{ext_part}"
            else:
                rotated_name = f"{base_name}_{timestamp}"
            
            rotated_path = os.path.join(log_dir, rotated_name)
            
            # Copy the current log to the rotated file
            shutil.copy2(log_path, rotated_path)
            
            # Compress if enabled
            if self.compress_rotated:
                try:
                    # Compress the rotated log
                    with open(rotated_path, 'rb') as f_in:
                        with gzip.open(f"{rotated_path}.gz", 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # Remove the uncompressed rotated log
                    os.remove(rotated_path)
                    rotated_path = f"{rotated_path}.gz"
                    logger.info(f"Compressed rotated log: {rotated_path}")
                except Exception as e:
                    logger.error(f"Error compressing log {rotated_path}: {str(e)}")
            
            # Clear the content of the original log file (but keep the file)
            with open(log_path, 'w') as f:
                f.write(f"Log rotated at {datetime.datetime.now()} - See {rotated_name}\n")
            
            logger.info(f"Rotated log {log_path} to {rotated_path}")
            
            # Enforce maximum number of rotated logs for this module
            self._enforce_max_logs(base_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Error rotating log {log_path}: {str(e)}")
            return False
    
    def _enforce_max_logs(self, base_log_name):
        """
        Ensure we don't keep too many rotated logs for a module
        
        Args:
            base_log_name: Base log name to check
        """
        try:
            # Extract module name from log filename
            if "." in base_log_name:
                module_name = base_log_name.rsplit(".", 1)[0]
            else:
                module_name = base_log_name
            
            # Find all rotated logs for this module
            pattern = os.path.join(self.log_dir, f"{module_name}_*.log*")
            rotated_logs = glob.glob(pattern)
            
            # Sort by modification time (oldest first)
            rotated_logs.sort(key=lambda x: os.path.getmtime(x))
            
            # Delete oldest logs if we have too many
            while len(rotated_logs) > self.max_logs_per_module:
                oldest_log = rotated_logs.pop(0)
                try:
                    os.remove(oldest_log)
                    logger.info(f"Deleted old log to maintain limit: {oldest_log}")
                except Exception as e:
                    logger.error(f"Error deleting old log {oldest_log}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error enforcing max logs for {base_log_name}: {str(e)}")
    
    def clean_old_logs(self):
        """
        Delete logs older than the configured maximum age
        
        Returns:
            int: Number of logs deleted
        """
        if not os.path.exists(self.log_dir):
            logger.error(f"Log directory does not exist: {self.log_dir}")
            return 0
        
        logger.info("Starting old log cleanup")
        deleted_count = 0
        
        # Calculate the cutoff date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.max_log_age_days)
        cutoff_timestamp = cutoff_date.timestamp()
        
        # Get all log files in the log directory (including compressed ones)
        log_files = glob.glob(os.path.join(self.log_dir, "*.log*"))
        
        for log_path in log_files:
            try:
                # Skip current (non-rotated) logs
                if "_20" not in os.path.basename(log_path):
                    continue
                
                # Check log age
                mod_time = os.path.getmtime(log_path)
                
                if mod_time < cutoff_timestamp:
                    os.remove(log_path)
                    deleted_count += 1
                    logger.info(f"Deleted old log: {log_path}")
                    
            except Exception as e:
                logger.error(f"Error cleaning log {log_path}: {str(e)}")
        
        logger.info(f"Log cleanup complete: {deleted_count} logs deleted")
        return deleted_count
    
    def get_log_stats(self):
        """
        Get statistics about log usage
        
        Returns:
            dict: Statistics about log files
        """
        stats = {
            "total_logs": 0,
            "total_size_kb": 0,
            "oldest_log": None,
            "largest_log": None,
            "largest_log_size_kb": 0,
            "by_module": {}
        }
        
        if not os.path.exists(self.log_dir):
            return stats
        
        # Get all log files
        log_files = glob.glob(os.path.join(self.log_dir, "*.log*"))
        stats["total_logs"] = len(log_files)
        
        oldest_time = None
        
        for log_path in log_files:
            try:
                # Get log size
                size_kb = os.path.getsize(log_path) / 1024
                stats["total_size_kb"] += size_kb
                
                # Track largest log
                if size_kb > stats["largest_log_size_kb"]:
                    stats["largest_log"] = os.path.basename(log_path)
                    stats["largest_log_size_kb"] = size_kb
                
                # Track oldest log
                mod_time = os.path.getmtime(log_path)
                if oldest_time is None or mod_time < oldest_time:
                    oldest_time = mod_time
                    stats["oldest_log"] = os.path.basename(log_path)
                
                # Track by module
                base_name = os.path.basename(log_path)
                if "." in base_name:
                    module_name = base_name.rsplit(".", 1)[0]
                    # Remove timestamp for rotated logs
                    if "_20" in module_name:
                        module_name = module_name.split("_20")[0]
                else:
                    module_name = base_name
                
                if module_name not in stats["by_module"]:
                    stats["by_module"][module_name] = {
                        "count": 0,
                        "total_size_kb": 0
                    }
                
                module_stats = stats["by_module"][module_name]
                module_stats["count"] += 1
                module_stats["total_size_kb"] += size_kb
                
            except Exception as e:
                logger.error(f"Error getting stats for {log_path}: {str(e)}")
        
        # Round total size
        stats["total_size_kb"] = round(stats["total_size_kb"], 2)
        
        # Format oldest log date
        if oldest_time:
            oldest_date = datetime.datetime.fromtimestamp(oldest_time)
            stats["oldest_log_date"] = oldest_date.strftime("%Y-%m-%d %H:%M:%S")
        
        return stats
    
    def run_maintenance(self):
        """
        Run all log maintenance tasks
        
        Returns:
            dict: Results of maintenance operations
        """
        logger.section("Running Log Maintenance")
        
        results = {
            "rotated": 0,
            "deleted": 0,
            "stats_before": self.get_log_stats(),
        }
        
        # Check if log management is enabled
        if not config_manager.is_enabled('log_management.enabled'):
            logger.info("Log management is disabled in configuration")
            results["stats_after"] = results["stats_before"]
            results["skipped"] = True
            return results
        
        # First rotate logs that are too large (if enabled)
        if config_manager.is_enabled('log_management.auto_rotate'):
            results["rotated"] = self.rotate_logs()
        else:
            logger.info("Log rotation is disabled in configuration")
        
        # Then clean up old logs (if enabled)
        if config_manager.is_enabled('log_management.auto_cleanup'):
            results["deleted"] = self.clean_old_logs()
        else:
            logger.info("Log cleanup is disabled in configuration")
        
        # Get stats after cleanup
        results["stats_after"] = self.get_log_stats()
        
        logger.info(f"Log maintenance complete: {results['rotated']} rotated, {results['deleted']} deleted")
        return results


# Create a singleton instance
log_manager = LogManager()


def run_log_maintenance():
    """
    Convenience function to run log maintenance
    
    Returns:
        dict: Results of maintenance operations
    """
    return log_manager.run_maintenance()


if __name__ == "__main__":
    # Run log maintenance if called directly
    print("Running log maintenance...")
    results = run_log_maintenance()
    
    # Print summary
    print(f"Log maintenance complete:")
    print(f"- Rotated {results['rotated']} logs")
    print(f"- Deleted {results['deleted']} old logs")
    print(f"- Total logs: {results['stats_after']['total_logs']}")
    print(f"- Total size: {results['stats_after']['total_size_kb']} KB")
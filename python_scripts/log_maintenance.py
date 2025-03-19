#!/usr/bin/env python3
"""
Standalone script for log maintenance tasks
Can be run from command line or as a scheduled task
"""
import sys
import os
import argparse
import json
from datetime import datetime

# Ensure the current directory is in the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # Import from common
    from common.log_manager import log_manager, run_log_maintenance
    from common.logger import get_logger
    from common.notification import send_telegram
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current path: {sys.path}")
    sys.exit(1)

# Set up logger
logger = get_logger("log_maintenance")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run log maintenance tasks")
    
    # Basic arguments
    parser.add_argument("--max-size", type=int, default=1024,
                        help="Maximum log size in KB before rotation (default: 1024)")
    parser.add_argument("--max-age", type=int, default=30,
                        help="Maximum log age in days before deletion (default: 30)")
    parser.add_argument("--max-logs", type=int, default=10,
                        help="Maximum number of rotated logs per module (default: 10)")
    parser.add_argument("--compress", action="store_true", default=True,
                        help="Compress rotated logs (default: True)")
    parser.add_argument("--no-compress", action="store_false", dest="compress",
                        help="Do not compress rotated logs")
    
    # Actions
    parser.add_argument("--stats-only", action="store_true",
                        help="Only show log statistics, don't perform maintenance")
    parser.add_argument("--notify", action="store_true",
                        help="Send notification after maintenance")
    parser.add_argument("--hass-token", help="Home Assistant token for notifications")
    
    # Output format
    parser.add_argument("--json", action="store_true",
                        help="Output results in JSON format")
    
    return parser.parse_args()


def update_manager_settings(args):
    """Update log manager settings from command line arguments"""
    # Update log manager settings
    log_manager.max_log_size_kb = args.max_size
    log_manager.max_log_age_days = args.max_age
    log_manager.max_logs_per_module = args.max_logs
    log_manager.compress_rotated = args.compress
    
    logger.info(f"Updated log manager settings: max_size={args.max_size}KB, max_age={args.max_age} days, "
                f"max_logs={args.max_logs}, compress={args.compress}")


def format_stats(stats):
    """Format log statistics for display"""
    output = "=== Log Statistics ===\n"
    output += f"Total logs: {stats['total_logs']}\n"
    output += f"Total size: {stats['total_size_kb']:.2f} KB\n"
    
    if stats['largest_log']:
        output += f"Largest log: {stats['largest_log']} ({stats['largest_log_size_kb']:.2f} KB)\n"
    
    if stats.get('oldest_log_date'):
        output += f"Oldest log: {stats['oldest_log']} ({stats['oldest_log_date']})\n"
    
    output += "\nBy module:\n"
    for module, module_stats in sorted(stats["by_module"].items()):
        output += f"  {module}: {module_stats['count']} logs, {module_stats['total_size_kb']:.2f} KB\n"
    
    return output


def send_notification(results, args):
    """Send notification about maintenance results"""
    if not args.hass_token:
        logger.error("No Home Assistant token provided for notification")
        return False
    
    try:
        # Format message
        message = "📊 *Log Maintenance Results*\n\n"
        message += f"Rotated logs: {results['rotated']}\n"
        message += f"Deleted logs: {results['deleted']}\n"
        message += f"Total logs: {results['stats_after']['total_logs']}\n"
        message += f"Total size: {results['stats_after']['total_size_kb']:.2f} KB\n"
        
        # Add space savings
        before_size = results['stats_before']['total_size_kb']
        after_size = results['stats_after']['total_size_kb']
        saved = before_size - after_size
        if saved > 0:
            message += f"Space saved: {saved:.2f} KB\n"
        
        # Send notification
        success = send_telegram(message, args.hass_token, markdown=True, title="Log Maintenance")
        
        if success:
            logger.info("Sent notification about maintenance results")
        else:
            logger.error("Failed to send notification")
        
        return success
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return False


def main():
    """Main function to run maintenance"""
    args = parse_arguments()
    
    try:
        # Update log manager settings
        update_manager_settings(args)
        
        # Get current stats
        stats = log_manager.get_log_stats()
        
        # Stats only mode
        if args.stats_only:
            if args.json:
                print(json.dumps(stats, indent=2))
            else:
                print(format_stats(stats))
            return 0
        
        # Run maintenance
        logger.section(f"Log Maintenance - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        results = run_log_maintenance()
        
        # Display results
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"Log maintenance complete:")
            print(f"- Rotated {results['rotated']} logs")
            print(f"- Deleted {results['deleted']} old logs")
            print(f"- Total logs: {results['stats_after']['total_logs']}")
            print(f"- Total size: {results['stats_after']['total_size_kb']:.2f} KB")
            
            # Calculate space saved
            before_size = results['stats_before']['total_size_kb']
            after_size = results['stats_after']['total_size_kb']
            if before_size > after_size:
                print(f"- Space saved: {before_size - after_size:.2f} KB")
        
        # Send notification if requested
        if args.notify and args.hass_token:
            send_notification(results, args)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during log maintenance: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
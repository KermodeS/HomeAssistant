"""
Common utilities for Home Assistant automation scripts
"""
from .config_manager import config_manager, ConfigManager
from .logger import get_logger
from .notification import send_telegram, notification_manager
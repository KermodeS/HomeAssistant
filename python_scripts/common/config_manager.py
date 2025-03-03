#!/usr/bin/env python3
"""
Configuration manager for Home Assistant automation scripts
Handles loading feature flags and providing access to configuration values
"""
import os
import yaml
import logging

# Set up basic logging for config manager
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("config_manager")


class ConfigManager:
    """Manages configuration and feature flags for automation scripts"""
    
    def __init__(self, config_path="/config/python_scripts/feature_flags.yaml"):
        """
        Initialize the config manager
        
        Args:
            config_path: Path to the feature flags YAML file
        """
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from the YAML file"""
        try:
            logger.info(f"Loading configuration from: {self.config_path}")
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as file:
                    self.config = yaml.safe_load(file)
                    if not self.config:
                        logger.warning("Config file exists but is empty, using empty dict")
                        self.config = {}
                    else:
                        logger.info(f"Loaded configuration with {len(self.config)} sections")
                        # Log first level keys to help with debugging
                        logger.info(f"Config sections: {', '.join(self.config.keys())}")
            else:
                logger.warning(f"Configuration file not found: {self.config_path}")
                self.config = {}
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self.config = {}
    
    def is_enabled(self, feature_path):
        """
        Check if a feature is enabled
        
        Args:
            feature_path: Dot notation path to feature (e.g., 'weather.daily_forecast')
            
        Returns:
            bool: True if feature is enabled, False otherwise
        """
        # First check if the parent feature is enabled
        parts = feature_path.split('.')
        if len(parts) > 1:
            parent = parts[0]
            parent_enabled = self.get_config_value(f"{parent}.enabled", True)
            if not parent_enabled:
                logger.debug(f"Parent feature {parent} is disabled, so {feature_path} is disabled")
                return False
        
        # Get the specific feature value
        enabled = self.get_config_value(feature_path, False)
        logger.debug(f"Feature {feature_path} enabled: {enabled}")
        return enabled
    
    def get_config_value(self, path, default=None):
        """
        Get a configuration value using dot notation
        
        Args:
            path: Dot notation path to configuration value
            default: Default value if path doesn't exist
            
        Returns:
            The configuration value or default
        """
        parts = path.split('.')
        value = self.config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                logger.debug(f"Config path {path} not found, returning default: {default}")
                return default
        
        logger.debug(f"Config path {path} = {value}")
        return value
    
    def __str__(self):
        """String representation of the config manager"""
        return f"ConfigManager(path={self.config_path}, sections={list(self.config.keys())})"


# Create a singleton instance for use throughout the application
config_manager = ConfigManager()


if __name__ == "__main__":
    # Test the config manager
    print("Testing ConfigManager...")
    print(f"Weather enabled: {config_manager.is_enabled('weather.enabled')}")
    print(f"Daily forecast enabled: {config_manager.is_enabled('weather.daily_forecast')}")
    print(f"Telegram enabled: {config_manager.is_enabled('notifications.telegram_enabled')}")
    
    # Print the complete configuration
    print("\nComplete Configuration:")
    for section, values in config_manager.config.items():
        print(f"  {section}:")
        for key, value in values.items():
            print(f"    {key}: {value}")
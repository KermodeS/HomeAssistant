#!/bin/bash
# Script to setup and validate directory structure for Home Assistant Python scripts

# Base directory
BASE_DIR="/config/python_scripts"
LOGS_DIR="/config/www/logs"

# Set up colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to create directory if it doesn't exist
create_dir() {
    if [ ! -d "$1" ]; then
        echo -e "${YELLOW}Creating directory: $1${NC}"
        mkdir -p "$1"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Directory created successfully${NC}"
        else
            echo -e "${RED}✗ Failed to create directory${NC}"
        fi
    else
        echo -e "${GREEN}✓ Directory already exists: $1${NC}"
    fi
}

# Function to create empty file if it doesn't exist
create_file() {
    if [ ! -f "$1" ]; then
        echo -e "${YELLOW}Creating empty file: $1${NC}"
        touch "$1"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ File created successfully${NC}"
        else
            echo -e "${RED}✗ Failed to create file${NC}"
        fi
    else
        echo -e "${GREEN}✓ File already exists: $1${NC}"
    fi
}

# Function to create standard __init__.py file
create_init_file() {
    if [ ! -f "$1/__init__.py" ]; then
        echo -e "${YELLOW}Creating __init__.py in: $1${NC}"
        echo '"""
'$2'
"""' > "$1/__init__.py"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ __init__.py created successfully${NC}"
        else
            echo -e "${RED}✗ Failed to create __init__.py${NC}"
        fi
    else
        echo -e "${GREEN}✓ __init__.py already exists in: $1${NC}"
    fi
}

# Create main directories
echo -e "${BLUE}Setting up directory structure...${NC}"
create_dir "$BASE_DIR"
create_dir "$BASE_DIR/common"
create_dir "$BASE_DIR/services"
create_dir "$BASE_DIR/debug"
create_dir "$LOGS_DIR"

# Create __init__.py files
create_init_file "$BASE_DIR" "Home Assistant automation scripts"
create_init_file "$BASE_DIR/common" "Common utilities for Home Assistant automation scripts"
create_init_file "$BASE_DIR/services" "Service modules for Home Assistant automation"
create_init_file "$BASE_DIR/debug" "Debug utilities for Home Assistant automation scripts"

# Set permissions
echo -e "${BLUE}Setting file permissions...${NC}"
chmod +x "$BASE_DIR/run.py" 2>/dev/null
chmod +x "$BASE_DIR/run_wrapper.sh" 2>/dev/null
chmod +x "$BASE_DIR/diagnose.py" 2>/dev/null
echo -e "${GREEN}✓ Permissions set${NC}"

# Create feature_flags.yaml if it doesn't exist
if [ ! -f "$BASE_DIR/feature_flags.yaml" ]; then
    echo -e "${YELLOW}Creating feature_flags.yaml...${NC}"
    echo '# Feature Flags for Home Assistant Automations
# Set to true to enable or false to disable features

weather:
  enabled: true  # Master switch for all weather features
  daily_forecast: true  # Daily temperature forecast
  extreme_weather_alert: true  # Notifications for rain, wind, snow

devices:
  enabled: true  # Master switch for all device monitoring
  shelly_caldaia_notifications: true  # Shelly relay status notifications

grocy:
  enabled: true  # Master switch for Grocy integration
  chores_notification: true  # Daily chores notifications

notifications:
  telegram_enabled: true  # Enable/disable all Telegram notifications
  log_to_file: true  # Log notifications to file for debugging

debug:
  verbose_logging: true  # Enable detailed logging' > "$BASE_DIR/feature_flags.yaml"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ feature_flags.yaml created successfully${NC}"
    else
        echo -e "${RED}✗ Failed to create feature_flags.yaml${NC}"
    fi
else
    echo -e "${GREEN}✓ feature_flags.yaml already exists${NC}"
fi

echo -e "${BLUE}Directory setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Place your Python modules in the appropriate directories"
echo -e "2. Run the diagnose.py script to verify everything is working correctly"
echo -e "3. Test your modules individually before enabling automations"
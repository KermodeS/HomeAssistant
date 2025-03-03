#!/bin/bash
# Script to set up the Python package structure and fix file names

# Base directory 
BASE_DIR="/config/python_scripts"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR"

# Create main package structure
mkdir -p common
mkdir -p services
mkdir -p debug

# Create __init__.py files
touch __init__.py
touch common/__init__.py
touch services/__init__.py
touch debug/__init__.py

# Fix misspelled filenames
# Check for pythin_script-* files and rename them
for file in pythin_script-*; do
    if [ -f "$file" ]; then
        new_name="${file/pythin_script-/python_script-}"
        echo "Renaming $file to $new_name"
        mv "$file" "$new_name"
    fi
done

# Move files to proper locations
# Common modules
echo "Setting up common modules..."
mv python_script-common-*.py common/ 2>/dev/null || true
mv python_script-common-__init__.py common/__init__.py 2>/dev/null || true
mv python_script-common-config_manager.py common/config_manager.py 2>/dev/null || true
mv python_script-common-logger.py common/logger.py 2>/dev/null || true
mv python_script-common-notification.py common/notification.py 2>/dev/null || true

# Service modules
echo "Setting up service modules..."
mv python_script-services-*.py services/ 2>/dev/null || true
mv python_script-services-__init__.py services/__init__.py 2>/dev/null || true
mv python_script-services-grocy.py services/grocy.py 2>/dev/null || true
mv python_script-services-weather.py services/weather.py 2>/dev/null || true
mv python_script-services-devices.py services/devices.py 2>/dev/null || true

# Debug modules
echo "Setting up debug modules..."
mv python_script-debug-*.py debug/ 2>/dev/null || true
mv python_script-debug-__init__.py debug/__init__.py 2>/dev/null || true
mv python_script-debug-grocy_debug.py debug/grocy_debug.py 2>/dev/null || true
mv python_script-debug-telegram_debug.py debug/telegram_debug.py 2>/dev/null || true

# Move the main run.py file
echo "Setting up main scripts..."
mv run.py.txt run.py 2>/dev/null || true
mv test_run.py.txt test_run.py 2>/dev/null || true
mv token_reader.py.txt token_reader.py 2>/dev/null || true

# Copy feature flags to the correct location
echo "Setting up configuration files..."
mv feature_flag.yaml.txt feature_flags.yaml 2>/dev/null || true

# Set execution permissions
echo "Setting execution permissions..."
chmod +x run.py
chmod +x test_run.py
chmod +x token_reader.py
chmod +x common/*.py
chmod +x services/*.py
chmod +x debug/*.py

# Create logs directory
echo "Creating logs directory..."
mkdir -p /config/www/logs

# Create a wrapper script to set PYTHONPATH
echo "Creating wrapper script..."
cat > run_wrapper.sh << 'EOF'
#!/bin/bash
# Wrapper script to ensure correct PYTHONPATH

# Set path to the python_scripts directory
export PYTHONPATH="/config/python_scripts:$PYTHONPATH"

# Run the actual Python script with all arguments
python3 /config/python_scripts/run.py "$@"
EOF

chmod +x run_wrapper.sh

echo "Setup complete!"
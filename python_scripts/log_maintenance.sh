#!/bin/bash
# Wrapper script for log maintenance

# Set path to the python_scripts directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Create logs directory if it doesn't exist
LOG_DIR="/config/www/logs"
mkdir -p "$LOG_DIR"

# Log file for this run
TIMESTAMP=$(date "+%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/log_maintenance_$TIMESTAMP.log"

# Log start
echo "Starting log maintenance at $(date)" | tee -a "$LOG_FILE"
echo "PYTHONPATH=$PYTHONPATH" >> "$LOG_FILE"

# Run the maintenance script
python3 "${SCRIPT_DIR}/log_maintenance.py" "$@" | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

# Log completion
echo "Log maintenance completed with exit code $EXIT_CODE at $(date)" | tee -a "$LOG_FILE"

# Update permissions
chmod 644 "$LOG_FILE"

exit $EXIT_CODE
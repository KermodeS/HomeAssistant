#!/bin/bash
# Wrapper script to ensure correct PYTHONPATH and handle redirection

# Set path to the python_scripts directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Create logs directory if it doesn't exist
LOG_DIR="/config/www/logs"
mkdir -p "$LOG_DIR"

# Log the execution details
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
echo "$TIMESTAMP: Running with PYTHONPATH=$PYTHONPATH" >> "$LOG_DIR/wrapper.log"
echo "$TIMESTAMP: Arguments: $@" >> "$LOG_DIR/wrapper.log"

# Determine log file based on mode
MODE=""
for i in "$@"; do
  if [[ $i == "--mode" ]]; then
    MODE_FLAG=true
  elif [[ $MODE_FLAG == true ]]; then
    MODE=$i
    MODE_FLAG=false
  fi
done

# Set the log file based on mode
if [[ "$MODE" == "grocy" ]]; then
  LOG_FILE="$LOG_DIR/grocy_run.log"
elif [[ "$MODE" == "weather" ]]; then
  LOG_FILE="$LOG_DIR/weather_run.log"
elif [[ "$MODE" == "device" ]]; then
  LOG_FILE="$LOG_DIR/device_run.log"
else
  LOG_FILE="$LOG_DIR/automation_run.log"
fi

echo "$TIMESTAMP: Using log file: $LOG_FILE" >> "$LOG_DIR/wrapper.log"
echo "$TIMESTAMP: Debug - Checking if mode $MODE is valid" >> "$LOG_DIR/wrapper.log"
echo "$TIMESTAMP: Debug - Full command: /usr/bin/python3 \"${SCRIPT_DIR}/run.py\" $@" >> "$LOG_DIR/wrapper.log"

# Run the actual Python script with all arguments and redirect output to the log file
echo "===== STARTING RUN AT $TIMESTAMP =====" > "$LOG_FILE"
python3 "${SCRIPT_DIR}/run.py" "$@" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Log exit code
echo "$TIMESTAMP: Exit code: $EXIT_CODE" >> "$LOG_DIR/wrapper.log"

# Append exit code to the log file as well
echo "===== FINISHED RUN AT $(date "+%Y-%m-%d %H:%M:%S") =====" >> "$LOG_FILE"
echo "Exit Code: $EXIT_CODE" >> "$LOG_FILE"

# Rotate log files if they get too large (>100KB)
if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE") -gt 102400 ]; then
  mv "$LOG_FILE" "${LOG_FILE}.old"
  echo "$TIMESTAMP: Rotated log file due to size" >> "$LOG_DIR/wrapper.log"
fi

exit $EXIT_CODE
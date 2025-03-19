#!/bin/bash
# Script to test shell commands for Home Assistant

# Output file for results
OUTPUT_FILE="/config/www/logs/shell_test.log"

# Create output file
echo "Shell Command Test Results" > $OUTPUT_FILE
echo "$(date)" >> $OUTPUT_FILE
echo "----------------------------------------" >> $OUTPUT_FILE

# Function to run a test and capture output
run_test() {
    local test_name="$1"
    local command="$2"
    
    echo "Testing: $test_name" | tee -a $OUTPUT_FILE
    echo "Command: $command" >> $OUTPUT_FILE
    echo "---------------------------------------" >> $OUTPUT_FILE
    echo "Output:" >> $OUTPUT_FILE
    
    # Run the command and capture output and return code
    output=$(eval "$command" 2>&1)
    ret_code=$?
    
    echo "$output" >> $OUTPUT_FILE
    echo "---------------------------------------" >> $OUTPUT_FILE
    echo "Return code: $ret_code" >> $OUTPUT_FILE
    echo "" >> $OUTPUT_FILE
    
    # Print summary to console
    if [ $ret_code -eq 0 ]; then
        echo "✅ Test passed: $test_name"
    else
        echo "❌ Test failed: $test_name (return code: $ret_code)"
    fi
}

# Read Home Assistant token
TOKEN_FILE="/config/token.txt"
if [ -f "$TOKEN_FILE" ]; then
    TOKEN=$(cat $TOKEN_FILE)
    echo "Found token file" | tee -a $OUTPUT_FILE
else
    echo "❌ Token file not found at $TOKEN_FILE" | tee -a $OUTPUT_FILE
    TOKEN="PLACEHOLDER_TOKEN"
fi

# Test Python scripts directly
echo "Testing Python scripts..." | tee -a $OUTPUT_FILE
run_test "Basic Python" "/usr/bin/python3 -c 'print(\"Hello world\")'"
run_test "Python version" "python3 --version"

# Test file existence
echo "Checking file existence..." | tee -a $OUTPUT_FILE
FILES_TO_CHECK=(
    "/config/python_scripts/run.py"
    "/config/python_scripts/feature_flags.yaml"
    "/config/python_scripts/common/__init__.py"
    "/config/python_scripts/common/config_manager.py"
    "/config/python_scripts/services/grocy.py"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ File exists: $file" | tee -a $OUTPUT_FILE
    else
        echo "❌ File missing: $file" | tee -a $OUTPUT_FILE
    fi
done

# Test specific module executions with full arguments
echo "Testing run.py with --debug flag..." | tee -a $OUTPUT_FILE
run_test "run.py Basic Test" "python3 /config/python_scripts/run.py --hass-token=\"$TOKEN\" --mode=grocy --grocy-url=\"http://192.168.1.128:9192\" --grocy-api-key=\"your-api-key\" --debug"

# Test shell commands (modified for testing)
echo "Testing shell commands..." | tee -a $OUTPUT_FILE
run_test "Test Token Reader" "python3 /config/python_scripts/token_reader.py"
run_test "Test Run Wrapper" "bash /config/python_scripts/run_wrapper.sh --hass-token=\"$TOKEN\" --mode=grocy --grocy-url=\"http://192.168.1.128:9192\" --grocy-api-key=\"your-api-key\" --debug"

echo "Test completed. Results saved to $OUTPUT_FILE"
echo "You can view the results with: cat $OUTPUT_FILE"
#!/bin/bash
# Script to check log files and update Home Assistant sensors

# Get the token
TOKEN=$(cat /config/token.txt)
if [ -z "$TOKEN" ]; then
  echo "Error: No token found"
  exit 1
fi

# Check weather log
if [ -f "/config/www/logs/weather_run.log" ]; then
  if grep -q 'Exit Code: 0' /config/www/logs/weather_run.log; then
    curl -s -X POST -H "Content-Type: application/json" http://localhost:8123/api/states/sensor.weather_run_status -H "Authorization: Bearer $TOKEN" -d '{"state": "success"}'
  else
    curl -s -X POST -H "Content-Type: application/json" http://localhost:8123/api/states/sensor.weather_run_status -H "Authorization: Bearer $TOKEN" -d '{"state": "failed"}'
  fi
else
  echo "Warning: Weather log file not found"
  curl -s -X POST -H "Content-Type: application/json" http://localhost:8123/api/states/sensor.weather_run_status -H "Authorization: Bearer $TOKEN" -d '{"state": "unknown"}'
fi

# Check grocy log
if [ -f "/config/www/logs/grocy_run.log" ]; then
  if grep -q 'Exit Code: 0' /config/www/logs/grocy_run.log; then
    curl -s -X POST -H "Content-Type: application/json" http://localhost:8123/api/states/sensor.grocy_run_status -H "Authorization: Bearer $TOKEN" -d '{"state": "success"}'
  else
    curl -s -X POST -H "Content-Type: application/json" http://localhost:8123/api/states/sensor.grocy_run_status -H "Authorization: Bearer $TOKEN" -d '{"state": "failed"}'
  fi
else
  echo "Warning: Grocy log file not found"
  curl -s -X POST -H "Content-Type: application/json" http://localhost:8123/api/states/sensor.grocy_run_status -H "Authorization: Bearer $TOKEN" -d '{"state": "unknown"}'
fi
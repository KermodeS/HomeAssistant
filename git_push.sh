#!/bin/bash
# Save to /config/git_push.sh

MAX_RETRIES=5
RETRY_DELAY=10
LOG_FILE="/config/git_push.log"

echo "===== Git Push Started: $(date) =====" >> $LOG_FILE

cd /config

# Add all changes
git add . >> $LOG_FILE 2>&1
git_status=$?

if [ $git_status -ne 0 ]; then
  echo "Error on git add: $git_status" >> $LOG_FILE
  exit 1
fi

# Commit if there are changes
git diff --staged --quiet
if [ $? -ne 0 ]; then
  git commit -m "Auto-commit: $(date)" >> $LOG_FILE 2>&1
  commit_status=$?
  
  if [ $commit_status -ne 0 ]; then
    echo "Error on git commit: $commit_status" >> $LOG_FILE
    exit 1
  fi
else
  echo "No changes to commit" >> $LOG_FILE
fi

# Push with retries
for (( i=1; i<=MAX_RETRIES; i++ )); do
  echo "Push attempt $i of $MAX_RETRIES" >> $LOG_FILE
  git push origin modular-restructure >> $LOG_FILE 2>&1
  push_status=$?
  
  if [ $push_status -eq 0 ]; then
    echo "Push successful on attempt $i" >> $LOG_FILE
    exit 0
  else
    echo "Push failed with status $push_status, retrying in $RETRY_DELAY seconds..." >> $LOG_FILE
    sleep $RETRY_DELAY
  fi
done

echo "All push attempts failed" >> $LOG_FILE
exit 1
#!/usr/bin/env python3
"""
Simplified token reader script - reads token from a dedicated token file
"""
import sys
import os

# Function to read the token from a dedicated file
def get_token():
    token_path = "/config/token.txt"
    if os.path.exists(token_path):
        try:
            with open(token_path, 'r') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading token file: {str(e)}")
            return ""
    else:
        print("Token file not found")
        return ""

# If run directly, print the token
if __name__ == "__main__":
    token = get_token()
    # Don't print token to log for security reasons
    if token:
        sys.stdout.write(token)
        sys.exit(0)
    else:
        sys.stderr.write("Failed to get token")
        sys.exit(1)
#!/usr/bin/env python3
"""
Robust token reader script for Home Assistant
Reads token from token file and validates it
"""
import sys
import os
import requests

# Token file location
TOKEN_PATH = "/config/token.txt"
TOKEN_FALLBACK_PATH = "/config/secrets.yaml"  # Alternative location
HASS_URL = "http://localhost:8123"  # Home Assistant URL

def get_token():
    """
    Read the token from a dedicated file or fallback locations
    
    Returns:
        str: The token or empty string on failure
    """
    # Try the primary token path
    if os.path.exists(TOKEN_PATH):
        try:
            with open(TOKEN_PATH, 'r') as file:
                token = file.read().strip()
                if token:
                    # Validate token if it exists
                    if validate_token(token):
                        return token
                    else:
                        print("Token validation failed")
                else:
                    print("Token file is empty")
        except Exception as e:
            print(f"Error reading token file: {str(e)}")
    else:
        print(f"Token file not found at {TOKEN_PATH}")
    
    # Try fallback path if primary failed
    if os.path.exists(TOKEN_FALLBACK_PATH):
        try:
            with open(TOKEN_FALLBACK_PATH, 'r') as file:
                content = file.read()
                
                # Try to find a token in the secrets file
                if "grocy_script_token" in content:
                    token_line = [line for line in content.split('\n') if "grocy_script_token" in line]
                    if token_line:
                        token = token_line[0].split(':')[1].strip()
                        if token.startswith('"') and token.endswith('"'):
                            token = token[1:-1]
                        elif token.startswith("'") and token.endswith("'"):
                            token = token[1:-1]
                        
                        if token and validate_token(token):
                            # If we found a valid token in secrets, save it to the token file for next time
                            try:
                                with open(TOKEN_PATH, 'w') as token_file:
                                    token_file.write(token)
                                print(f"Token saved to {TOKEN_PATH}")
                            except Exception as e:
                                print(f"Error saving token: {str(e)}")
                            
                            return token
            
            print("No valid token found in secrets file")
        except Exception as e:
            print(f"Error reading secrets file: {str(e)}")
    
    return ""


def validate_token(token):
    """
    Validate if a token works with Home Assistant API
    
    Args:
        token: The token to validate
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    if not token:
        return False
    
    try:
        url = f"{HASS_URL}/api/config"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        return response.status_code == 200
    except Exception:
        return False


if __name__ == "__main__":
    token = get_token()
    if token:
        # Don't print token to stderr for security reasons
        sys.stdout.write(token)
        sys.exit(0)
    else:
        sys.stderr.write("Failed to get token")
        sys.exit(1)
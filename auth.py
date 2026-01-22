"""
Authentication module for Synology Surveillance Station.
Handles login and logout operations.
"""

from config import BASE_URL, AUTH_API_PATH, SYNOLOGY_USERNAME, SYNOLOGY_PASS
import requests


def login():
    """Login to Synology Surveillance Station and create session."""
    params = {
        'api': 'SYNO.API.Auth',
        'method': 'login',
        'version': '7',
        'account': SYNOLOGY_USERNAME,
        'passwd': SYNOLOGY_PASS,
        'session': 'SurveillanceStation',
        'format': 'sid'
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}{AUTH_API_PATH}",
            params=params, 
            timeout=10, 
            verify=False)
        
        response.raise_for_status()
        data = response.json()
        
        if data.get('success'):
            sid = data['data']['sid']
            print(f"[SUCCESS] Login successful")
            return sid
        else:
            error_code = data.get('error', {}).get('code')
            print(f"[ERROR] Login failed (API code:{error_code})")
            return None
            
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return None


def logout(sid):
    """Logout from Synology Surveillance Station and close session."""
    if not sid:
        print("[ERROR] Invalid session ID for logout")
        return False
    
    params = {
        'api': 'SYNO.API.Auth',
        'method': 'logout',
        'version': '7',
        'session': 'SurveillanceStation',
        '_sid': sid
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}{AUTH_API_PATH}",
            params=params, 
            timeout=10, 
            verify=False)
        
        response.raise_for_status()
        data = response.json()
        
        if data.get('success'):
            print("[SUCCESS] Logout successful")
            return True
        else:
            errno = data.get('error', {}).get('code')
            print(f"[ERROR] Logout failed with API code: {errno})")
            return False
            
    except Exception as e:
        print(f"[ERROR] Logout failed: {e}")
        return False

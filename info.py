"""
Info module for Synology Surveillance Station.
Handles API information retrieval operations.
"""

import requests
import json
from config import BASE_URL, INFO_API_PATH


def get_info(sid):
    """Display information about available Surveillance Station APIs."""
    params = {
        'api': 'SYNO.API.Info',
        'method': 'Query',
        'version': '1',
        'query': 'SYNO.SurveillanceStation.Info, '
                 'SYNO.SurveillanceStation.PTZ, '
                 'SYNO.SurveillanceStation.Camera, '
                 'SYNO.SurveillanceStation.SnapShot, '
                 'SYNO.SurveillanceStation.Recording, '
                 'SYNO.SurveillanceStation.Auth',
        '_sid': sid
    }
    
    try:
        response = requests.get(f"{BASE_URL}{INFO_API_PATH}", params=params, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success'):
            print("\n[INFO] Available APIs:")
            print(json.dumps(data['data'], indent=4))
        else:
            errno = data.get('error', {}).get('code')
            print(f"[ERROR] API info query failed with API code: {errno}")
            
    except Exception as e:
        print(f"[ERROR] API info retrieval failed: {e}")

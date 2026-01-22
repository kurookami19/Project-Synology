"""
Recorrding module for Synology Surveillance Station.
Handles List and Download operations.
"""

import requests
from config import BASE_URL, CAMERA_API_PATH


def rec_list(sid):
    params = {
        'api' : 'SYNO.SurveillanceStation.Recording',
        'method' : 'List',
        'version' : '6',
        '_sid' : sid,
        'limit': 50
    }
    try:
        response = requests.get(f"{BASE_URL}{CAMERA_API_PATH}", params = params, timeout = 10, verify = False)
        response.raise_for_status()
        data = response.json()

        if data.get('success'):
            recs = data["data"].get("recordings", [])
            return recs
        else:
            errno = data.get('error', {}).get('code')
            print(f"Recording List failed with API code: {errno}")
            return None
    except Exception as e:
        print(f"[ERROR] Recording list failed: {e}")
        return None
    
def rec_download(sid, rec_id, file_name):
    """Download a recording by ID with progress bar."""
    params = {
        'api': 'SYNO.SurveillanceStation.Recording',
        'method': 'Download',
        'version': '6',
        '_sid': sid,
        'id': rec_id
    }
    
    try:
        response = requests.get(f"{BASE_URL}{CAMERA_API_PATH}/{file_name}", params=params, timeout=120, verify=False, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        
        if 'video' in content_type or 'octet-stream' in content_type:
            total_size = int(response.headers.get('Content-Length', 0))
            
            print(f"\n[INFO] Downloading recording {rec_id}...")
            if total_size > 0:
                print(f"[INFO] File size: {total_size / (1024 * 1024):.2f} MB")
            
            with open(file_name, 'wb') as f:
                downloaded = 0
                # 512 KB = 524288 bytes (ottimo per file 100-200MB)
                # 1 MB = 1048576 bytes (ottimo per file >200MB)
                chunk_size = 1024 * 1024  # 1 MB
                
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            bar_length = 40
                            filled = int(bar_length * downloaded / total_size)
                            bar = '█' * filled + '-' * (bar_length - filled)
                            print(f"\r[{bar}] {percent:.1f}%", end='', flush=True)
                        else:
                            print(f"\rDownloaded: {downloaded / (1024 * 1024):.2f} MB", 
                                  end='', flush=True)
            
            print(f"\n[SUCCESS] Recording saved: {file_name}")
            return file_name
        
        else:
            try:
                data = response.json()
                errno = data.get('error', {}).get('code', 'unknown')
                print(f"[ERROR] Recording download failed with API code: {errno}")
            except:
                print(f"[ERROR] Unknown response type: {content_type}")
            
            return None
            
    except Exception as e:
        print(f"[ERROR] Recording download failed: {e}")
        return None
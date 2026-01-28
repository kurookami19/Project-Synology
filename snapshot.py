"""
Snapshot management module for Synology Surveillance Station.
Handles snapshot capture, save, download, and display operations.
"""

from config import BASE_URL, CAMERA_API_PATH
import requests
import base64
from PIL import Image
import io
import json


def take_snapshot(sid, camId, dsId):
    """Capture a snapshot from the camera without saving to database."""
    params = {
        'api': 'SYNO.SurveillanceStation.SnapShot',
        'method': 'TakeSnapshot',
        'version': '1',
        '_sid': sid,
        'camId': camId,
        'dsId': dsId,
        'blSave': 'false'
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}{CAMERA_API_PATH}", 
            params=params, 
            timeout=10, 
            verify=False)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            errno = data.get('error', {}).get('code')
            print(f"[ERROR] Snapshot capture failed "
                  f"with API code: {errno}")
            return None
        
        return data['data']
        
    except Exception as e:
        print(f"[ERROR] Snapshot capture failed: {e}")
        return None


def save_snapshot(sid, snapData):
    """Save a captured snapshot to Synology database."""
    params = {
        'api': 'SYNO.SurveillanceStation.SnapShot',
        'method': 'Save',
        'version': '1',
        '_sid': sid
    }
    
    data = {
        'camName': snapData.get('camName', ''),
        'createdTm': snapData.get('createdTm', 0),
        'width': snapData.get('width', 0),
        'height': snapData.get('height', 0),
        'byteSize': snapData.get('byteSize', 0),
        'imageData': snapData.get('imageData', '')
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}{CAMERA_API_PATH}", 
            params=params, 
            data=data, 
            timeout=30, 
            verify=False)
        response.raise_for_status()
        result = response.json()
        
        if not result.get('success'):
            errno = result.get('error', {}).get('code')
            print(f"[ERROR] Snapshot save failed with API code: {errno}")
            return None
        
        snapshot_id = result['data'].get('snapshotId')
        return snapshot_id
        
    except Exception as e:
        print(f"[ERROR] Snapshot save failed: {e}")
        return None


def get_snapshot_list(sid, camId):
    """Get list of saved snapshots for a specific camera."""
    params = {
        'api': 'SYNO.SurveillanceStation.SnapShot',
        'method': 'List',
        'version': '1',
        '_sid': sid,
        'start': 0,
        'limit': 0,
        'from': 0,
        'to': 0,
        'blIncludeRecCnt': 'false',
        'blIncludeAuInfo': 'false',
        'camId': camId
    }
    
    try:
        response = requests.get(f"{BASE_URL}{CAMERA_API_PATH}", params=params, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            errno = data.get('error', {}).get('code')
            print(f"[ERROR] Snapshot list retrieval failed with API code: {errno}")
            return None
        
        snapshots = data['data'].get('data', [])
        total = data['data'].get('total', 0)
        
        print(f"[INFO] Found {total} total snapshots")
        return snapshots
        
    except Exception as e:
        print(f"[ERROR] Snapshot list retrieval failed: {e}")
        return None


def download_snapshot(sid, snap_id, save_path):
    """Download a saved snapshot by ID to local file."""
    params = {
        'api': 'SYNO.SurveillanceStation.SnapShot',
        'method': 'Download',
        'version': '1',
        '_sid': sid,
        'id': snap_id
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}{CAMERA_API_PATH}", 
            params=params, 
            timeout=30, 
            verify=False)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        
        if 'image' in content_type or len(response.content) > 1000:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"[SUCCESS] Image downloaded: {save_path} "
                  f"({len(response.content)} bytes)")
            return save_path
        else:
            try:
                data = response.json()
                errno = data.get('error', {}).get('code')
                print(f"[ERROR] Snapshot download failed "
                      f"with API code: {errno}")
            except:
                print(f"[ERROR] Unknown response received")
            
            return None
            
    except Exception as e:
        print(f"[ERROR] Snapshot download failed: {e}")
        return None


def show_snapshot(snapData):
    """Decode and display snapshot image from base64 data."""
    try:
        image_base64 = snapData['imageData']
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        
        print("\nSnapshot Preview:")
        print(f"  Camera:     {snapData.get('camName', 'Unknown')}")
        print(f"  Resolution: {snapData.get('width', 0)}"
              f"x{snapData.get('height', 0)}")
        print(f"  Size:       {snapData.get('byteSize', 0)} bytes")
        
        image.show()
        
    except Exception as e:
        print(f"[ERROR] Failed to display snapshot: {e}")


def delete_snapshots(sid, id_list):
    """Delete snapshots by ID list"""
    
    # Costruisci l'array di oggetti
    objList = [{"id": f"0:{snap_id}"} for snap_id in id_list]
    
    params = {
        'api': 'SYNO.SurveillanceStation.SnapShot',
        'method': 'Delete',
        'version': '1',
        '_sid': sid,
        'objList': json.dumps(objList)
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}{CAMERA_API_PATH}",
            params=params,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        data = response.json()
        
        if not data.get('success'):
            errno = data.get('error', {}).get('code')
            print(f"[ERROR] Snapshot deletion failed "
                  f"with API code: {errno}")
            return False
        
        print(f"[SUCCESS] Successfully deleted"
              f" {len(id_list)} snapshot(s)")
        return True
        
    except Exception as e:
        print(f"[ERROR] Snapshot deletion failed: {e}")
        return False

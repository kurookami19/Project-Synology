"""
Camera module for Synology Surveillance Station.
Handles camera list and live path retrieval operations.
"""

import requests
from config import BASE_URL, CAMERA_API_PATH


def get_cameras_list(sid):
    """Get list of all connected cameras."""
    params = {
        'api': 'SYNO.SurveillanceStation.Camera',
        'method': 'List',
        'version': '9',
        '_sid': sid,
        'privCamType': 0,
        'camStm': 0,
        'basic': 'true'
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
            print(f"[ERROR] List failed with API code: {errno}")
            return None
        
        cameras = data['data'].get('cameras', [])
        
        # Display camera info
        print(f"\n[INFO] Cameras found: {len(cameras)}")
        for cam in cameras:
            print(f"Camera: {cam.get('model'):20} | "
                  f"ID: {cam.get('id'):3} | "
                  f"dsId: {cam.get('dsId')} | "
                  f"Codec: {cam.get('videoCodec')} | "
                  f"Vendor: {cam.get('vendor')}")
        
        return cameras 
        
    except Exception as e:
        print(f"[ERROR] Camera list retrieval failed: {e}")
        return None
    

def get_capability_by_cam_id(sid, camId):
    params = {
        'api': 'SYNO.SurveillanceStation.Camera',
        'method': 'GetCapabilityByCamId',
        'version': '8',      
        'cameraId': camId,   
        '_sid': sid
    }

    try:
        response = requests.get(
            f"{BASE_URL}{CAMERA_API_PATH}", 
            params=params,
            timeout=10, 
            verify=False)
        
        response.raise_for_status()
        data = response.json()
        
        if data.get('success'):
            return data.get('data')
        else:
            errno = data.get('error', {}).get('code')
            print(f"[ERROR] Get Capability failed with "
                  f"API code: {errno}")
            return None

    except Exception as e:
        print(f"[ERROR] Get capability failed: {e}")
        return None


def get_live_path(sid, camId):
    """Get Live paths of the specified camera(s)"""
    params = {
        'api': "SYNO.SurveillanceStation.Camera",
        'method': "GetLiveViewPath",
        'version': '9',
        '_sid': sid,
        'idList': str(camId)
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
            print(f"[ERROR] GetLiveViewPath failed with "
                  f"API code: {errno}")
            return None
        
        camera_paths = data['data'][0] if data.get('data') else {}
        
        # Display live paths info
        print(f"\n[INFO] Live paths for "
              f"Camera ID: {camera_paths.get('id')}")
        print(f"  RTSP Path:       "
              f"{camera_paths.get('rtspPath', 'N/A')}")
        print(f"  RTSP over HTTP:  "
              f"{camera_paths.get('rtspOverHttpPath', 'N/A')}")
        print(f"  MJPEG HTTP:      "
              f"{camera_paths.get('mjpegHttpPath', 'N/A')}")
        print(f"  MXPEG HTTP:      "
              f"{camera_paths.get('mxpegHttpPath', 'N/A')}")
        print(f"  Multicast:       "
              f"{camera_paths.get('multicstPath', 'N/A')}")
        
        # Return Main parameters
        return {
            'camera_id': camera_paths.get('id'),
            'rtsp_path': camera_paths.get('rtspPath', ''),
            'rtsp_Ohttp':camera_paths.get('rtspOverHttpPath',''),
            'mjpeg_http': camera_paths.get('mjpegHttpPath', ''),
            'mxpeg_http': camera_paths.get('mxpegHttpPath', ''),
            'multicast_path': camera_paths.get('multicstPath', '')
        }

    except Exception as e:
        print(f"[ERROR] GetLiveViewPath failed: {e}")
        return None

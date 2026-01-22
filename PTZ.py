"""
PTZ module for Synology Surveillance Station.
Handles PTZ camera movement and preset operations.
"""

import requests
from pynput import keyboard
import threading
from config import BASE_URL, CAMERA_API_PATH


def show_preset(sid, camId):
    """Get list of PTZ presets for a camera."""
    params = {
        'api': 'SYNO.SurveillanceStation.PTZ',
        'method': 'ListPreset',
        'version': '1',
        '_sid': sid,
        'cameraId': camId
    }
    
    try:
        response = requests.get(f"{BASE_URL}{CAMERA_API_PATH}", params=params, timeout=10, verify=False)
        response.raise_for_status()
        data = response.json()
        
        if data.get('success'):
            presets = data['data'].get('presets', [])
            return presets
        else:
            errno = data.get('error', {}).get('code')
            print(f"[ERROR] Show preset failed with API code: {errno}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Show preset failed: {e}")
        return None


class PTZController:
    """Interactive PTZ camera controller using keyboard input."""
    
    def __init__(self, sid, cam_id):
        self.sid = sid
        self.cam_id = cam_id
        self.active_direction = None
        self.lock = threading.Lock()
    
    def ptz_move(self, direction, move_type):
        """Send PTZ move command to camera."""
        params = {
            'api': 'SYNO.SurveillanceStation.PTZ',
            'method': 'Move',
            'version': '3',
            '_sid': self.sid,
            'cameraId': self.cam_id,
            'direction': direction,
            'speed': 3,
            'moveType': move_type
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
                print(f"[INFO] PTZ Move {direction} ({move_type})")
            else:
                errno = data.get('error', {}).get('code')
                print(f"[ERROR] PTZ move failed with "
                      f"API code: {errno}")
                
        except Exception as e:
            print(f"[ERROR] PTZ move failed: {e}")
    
    def on_press(self, key):
        """Handle key press events."""
        with self.lock:
            try:
                # WASD keys
                if hasattr(key, 'char'):
                    if key.char == 'w' and self.active_direction != 'up':
                        self.active_direction = 'up'
                        self.ptz_move('up', 'Start')
                    elif key.char == 's' and self.active_direction != 'down':
                        self.active_direction = 'down'
                        self.ptz_move('down', 'Start')
                    elif key.char == 'a' and self.active_direction != 'left':
                        self.active_direction = 'left'
                        self.ptz_move('left', 'Start')
                    elif key.char == 'd' and self.active_direction != 'right':
                        self.active_direction = 'right'
                        self.ptz_move('right', 'Start')
                
                # Arrow keys
                elif key == keyboard.Key.up and self.active_direction != 'up':
                    self.active_direction = 'up'
                    self.ptz_move('up', 'Start')
                elif key == keyboard.Key.down and self.active_direction != 'down':
                    self.active_direction = 'down'
                    self.ptz_move('down', 'Start')
                elif key == keyboard.Key.left and self.active_direction != 'left':
                    self.active_direction = 'left'
                    self.ptz_move('left', 'Start')
                elif key == keyboard.Key.right and self.active_direction != 'right':
                    self.active_direction = 'right'
                    self.ptz_move('right', 'Start')
                    
            except AttributeError:
                pass
    
    def on_release(self, key):
        """Handle key release events."""
        with self.lock:
            should_stop = False
            
            try:
                if hasattr(key, 'char'):
                    if key.char in ['w', 's', 'a', 'd']:
                        should_stop = True
                elif key in [keyboard.Key.up, keyboard.Key.down, 
                           keyboard.Key.left, keyboard.Key.right]:
                    should_stop = True
            except AttributeError:
                pass
            
            if should_stop and self.active_direction:
                self.ptz_move(self.active_direction, 'Stop')
                self.active_direction = None
            
            # ESC to exit
            if key == keyboard.Key.esc:
                if self.active_direction:
                    self.ptz_move(self.active_direction, 'Stop')
                print("\n[INFO] Exiting PTZ controller")
                return False
    
    def start(self):
        """Start the PTZ controller."""
        print("\n" + "=" * 50)
        print("PTZ CONTROLLER".center(50))
        print("=" * 50)
        print("Controls:")
        print("  W / ↑ = Up    | S / ↓ = Down")
        print("  A / ← = Left  | D / → = Right")
        print("  ESC = Exit")
        print("=" * 50)
        print("\nHold key to move, release to stop\n")
        
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        ) as listener:
            listener.join()


def ptz_controller(sid, cam_id):
    """Initialize and start PTZ controller."""
    controller = PTZController(sid, cam_id)
    controller.start()

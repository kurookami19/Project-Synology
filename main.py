"""
Main entry point for Synology Surveillance Station API Client.
Provides an interactive CLI menu for camera management, snapshot capture, and recording download.
"""

from auth import login, logout
from info import get_info
from camera import get_cameras_list, get_capability_by_cam_id, get_live_path, enable, disable
from PTZ import show_preset, ptz_controller
from snapshot import take_snapshot, download_snapshot, get_snapshot_list, save_snapshot, show_snapshot, delete_snapshots
from recording import rec_list, rec_download


def print_header(title):
    """Print a formatted header with title."""
    print("\n" + "=" * 50)
    print(title.center(50))
    print("=" * 50)


def print_error(message):
    """Print a formatted error message."""
    print(f"[ERROR] {message}")


def print_success(message):
    """Print a formatted success message."""
    print(f"[SUCCESS] {message}")


def print_info(message):
    """Print a formatted info message."""
    print(f"[INFO] {message}")


def select_camera(cameras):
    while True:
        try:
            cam_input = input("\nWhich camera do you want to use?"
                              " (enter Camera ID): ")
            cam_id_selected = int(cam_input)
            
            for cam in cameras:
                if cam_id_selected == cam.get('id'):
                    cam_id = cam.get('id')
                    ds_id = cam.get('dsId')
                    print_success(f"Camera selected: ID={cam_id},"
                                  f" dsId={ds_id}")
                    return cam_id, ds_id
            
            print_error(f"Camera ID {cam_id_selected} not found. "
                        "Please try again.")
            
        except ValueError:
            print_error("Invalid input. "
                        "Please enter a valid integer.")
        except KeyboardInterrupt:
            print("\n[INFO] Camera selection cancelled")
            return None, None


def handle_api_info(sid):
    """Handle API info display."""
    get_info(sid)


def handle_camera_capability(sid, cam_id):
    """Handle camera capability display."""
    caps = get_capability_by_cam_id(sid, cam_id)
    if caps:
        print("\nCamera Capabilities:")
        print("(0 = No, 1 = Step, 2 = Continuous)")
        print(f"  PTZ Pan Support:   {caps.get('ptzPan')}")
        print(f"  PTZ Zoom Support:  {caps.get('ptzZoom')}")
        print(f"  Audio Out Support: {caps.get('audioOut')}")


def handle_ptz_control(sid, cam_id):
    """Handle PTZ camera movement."""
    print_info("Attempting to move camera...")
    ptz_controller(sid, cam_id)


def handle_snapshot_capture(sid, cam_id, ds_id):
    """Handle snapshot capture with preview and conditional save."""
    print_info("Capturing snapshot...")
    
    snap_data = take_snapshot(sid, cam_id, ds_id)
    
    if not snap_data:
        return
    
    show_snapshot(snap_data)
    print_success("Snapshot captured successfully!")
    
    print("\nDo you want to save this snapshot to Synology?")
    print("[Y] Yes    [N] No")
    choice = input("Choice: ").strip()
    
    if choice == "Y":
        snapshot_id = save_snapshot(sid, snap_data)
        if snapshot_id:
            print_success(f"Snapshot saved with ID: {snapshot_id}")
    elif choice == "N":
        print("Snapshot not saved.")
    else:
        print_error("Invalid choice. Snapshot not saved.")

def handle_snapshot_download(sid, cam_id):
    """Handle snapshot download by ID."""
    snap_list = get_snapshot_list(sid, cam_id)
    
    if not snap_list:
        return
    
    print("\nAvailable Snapshots:")
    for snap in snap_list:
        print(f"ID: {snap['id']:<5} | {snap['fileName']:^60} | Camera: {snap['camName']}")

    snap_dict = {snap['id']: snap for snap in snap_list}
    
    while True:
        snap_id_input = input('\nSnapshot ID to download (Q to exit): ').strip()
        
        if snap_id_input.upper() == 'Q':
            print_info("Exiting download menu")
            break
        
        if not snap_id_input.isdigit():
            print_error("Please enter a valid numeric ID")
            continue
        
        snap_id = int(snap_id_input)
        
        if snap_id not in snap_dict:
            print_error(f"ID {snap_id} not found")
            continue
        
        name_img = input('Filename (without extension): ').strip()
        
        if not name_img:
            print_error("Filename cannot be empty")
            continue
        
        result = download_snapshot(sid, snap_id, name_img + ".jpg")
        if result:
            break


def handle_recording_list(sid):
    """Handle recording list display."""
    print_info("Fetching recording list (max 50)...")
    
    recordings = rec_list(sid)
    
    if not recordings:
        print_info("No recordings found")
        return
    
    print("\nAvailable Recordings:")
    for rec in recordings:
        print(f"ID: {rec['id']:<10} | Camera ID: {rec['cameraId']}")


def handle_recording_download(sid):
    """Handle recording download by ID."""
    rec_id = input("Enter recording ID: ").strip()
    rec_name = input("Save file as (without extension): ").strip()
    
    if not rec_name:
        print_error("Filename cannot be empty")
        return
    
    print_info("Downloading recording...")
    rec_download(sid, rec_id, rec_name + ".mp4")


def handle_preset_list(sid, cam_id):
    """Handle PTZ preset list display."""
    presets = show_preset(sid, cam_id)
    
    if not presets:
        print_info("No presets available for this camera")
        return
    
    print("\nAvailable PTZ Presets:")
    for preset in presets:
        print(f"ID: {preset['id']:<5} | Name: {preset['name']}")


def handle_get_live_path(sid, cam_id):
    """"Handle Camera GetLiveViewPath"""
    livePath = get_live_path(sid, cam_id)

    if not livePath:
        print_info("No Live path of the live view for this camera")
        return
    

def handle_enable_disable_camera(sid, cam_id):
    """Handle camera disable or enable"""
    print(f"Do you want to enable or disable camera: {cam_id}?")
    print("[E]: Enable      [D]: Disable ")
    c = input()
    c = c.upper()
    if c == "E":
        enable(sid, cam_id)
    elif c == "D":
        disable(sid, cam_id)
    else:
        print("Invalid command.")


def handle_delete_snap(sid, cam_id):
    """handle delete snapshot by IDs"""
    snap_list = get_snapshot_list(sid, cam_id)
    
    if not snap_list:
        print_error("No snapshots found")
        return
    
    print("\nAvailable Snapshots:")
    for snap in snap_list:
        print(f"ID: {snap['id']:<5} | {snap['fileName']:^60} | Camera: {snap['camName']}")

    snap_dict = {snap['id']: snap for snap in snap_list}
    
    # Lista per raccogliere gli ID da eliminare
    ids_to_delete = []

    while True:
        snap_id_input = input('\nSnapshot ID to delete (Q when finished): ').strip()
        
        if snap_id_input.upper() == 'Q':
            break
        
        if not snap_id_input.isdigit():
            print_error("Please enter a valid numeric ID")
            continue
        
        snap_id = int(snap_id_input)
        
        if snap_id not in snap_dict:
            print_error(f"ID {snap_id} not found")
            continue
        
        # Controlla se l'ID è già stato aggiunto
        if snap_id in ids_to_delete:
            print(f"ID {snap_id} already marked for deletion")
            continue
        
        # Aggiungi alla lista
        ids_to_delete.append(snap_id)
        print_success(f"Snapshot {snap_id} ({snap_dict[snap_id]['fileName']}) marked for deletion")
    
    # Dopo l'uscita dal ciclo, elimina tutto
    if not ids_to_delete:
        print_info("No snapshots selected for deletion")
        return
    
    # Conferma finale
    print(f"\nAbout to delete {len(ids_to_delete)} snapshot(s):")
    for snap_id in ids_to_delete:
        print(f"{snap_id}: {snap_dict[snap_id]['fileName']}")
    
    confirm = input("\nConfirm deletion? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print_info("Deletion cancelled")
        return
    
    # Chiamata API Delete
    result = delete_snapshots(sid, ids_to_delete)
    
    if not result:
        print_error("Deletion failed")


def display_menu():
    """Display the main menu options."""
    print_header("MAIN MENU")
    print("[1] Get API Info")
    print("[2] Get Camera Capability")
    print("[3] Move Camera (PTZ)")
    print("[4] Take Snapshot and Save")
    print("[5] Delete Snapshot (by ID)")
    print("[6] Download Snapshot (by ID)")
    print("[7] Show Recording List")
    print("[8] Download Recording (by ID)")
    print("[9] Show List of PTZ Presets")
    print("[10] Show RTSP live Info")
    print("[11] Enable/Disable selected camera")
    print("[0] Logout and Exit")
    print("=" * 50)


def main():
    """Main function to run the Surveillance Station client."""
    
    print_header("SYNOLOGY SURVEILLANCE STATION API CLIENT")
    
    sid = None
    
    try:
        # Login
        print_info("Connecting to Synology NAS...")
        sid = login()
        
        if not sid:
            return
        
        # Get cameras
        cameras = get_cameras_list(sid)
        if not cameras:
            return
        
        # Select camera
        cam_id, ds_id = select_camera(cameras)
        if cam_id is None:
            print_error("No camera selected. Exiting.")
            return
        
        # Main menu loop
        while True:
            display_menu()
            command = input("Enter command: ").strip()
            
            if command == "1":
                handle_api_info(sid)
            elif command == "2":
                handle_camera_capability(sid, cam_id)
            elif command == "3":
                handle_ptz_control(sid, cam_id)
            elif command == "4":
                handle_snapshot_capture(sid, cam_id, ds_id)
            elif command == "5":
                handle_delete_snap(sid, cam_id)
            elif command == "6":
                handle_snapshot_download(sid, cam_id)
            elif command == "7":
                handle_recording_list(sid)
            elif command == "8":
                handle_recording_download(sid)
            elif command == "9":
                handle_preset_list(sid, cam_id)
            elif command == "10":
                handle_get_live_path(sid, cam_id)
            elif command == "11":
                handle_enable_disable_camera(sid, cam_id)
            elif command == "0":
                print_info("Exiting...")
                break
            else:
                print_error("Invalid command. Please use 0-10")
        
    except KeyboardInterrupt:
        print("\n[INFO] Program interrupted by user")
        
    except Exception as e:
        print_error(f"Fatal error occurred: {e}")
        
    finally:
        if sid:
            print_info("Disconnecting from NAS...")
            logout(sid)


if __name__ == "__main__":
    main()

import os
from dotenv import load_dotenv

load_dotenv()

print("SYNOLOGY_IP:", os.getenv("SYNOLOGY_IP"))
print("SYNOLOGY_PORT:", os.getenv("SYNOLOGY_PORT"))
print("SYNOLOGY_USERNAME:", os.getenv("SYNOLOGY_USERNAME"))
print("SYNOLOGY_PASS:", os.getenv("SYNOLOGY_PASS"))
print("CAMERA_ID:", os.getenv("CAMERA_ID"))

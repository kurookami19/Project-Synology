"""
Configuration module for Synology Surveillance Station API Client.
Loads environment variables from .env file and validates required settings.
"""

import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


# Synology NAS configuration
SYNOLOGY_IP = os.getenv('SYNOLOGY_IP', 'localhost')  # default 'localhost' if not defined
SYNOLOGY_PORT = int(os.getenv('SYNOLOGY_PORT', 5000))  # convert to int, default 5000
SYNOLOGY_USERNAME = os.getenv('SYNOLOGY_USERNAME', '')
SYNOLOGY_PASS = os.getenv('SYNOLOGY_PASS', '')


# Build base URL using IP and PORT variables
BASE_URL = f"http://{SYNOLOGY_IP}:{SYNOLOGY_PORT}"


# Validation: ensure credentials are configured
if not SYNOLOGY_USERNAME or not SYNOLOGY_PASS:
    raise ValueError(
        "Username and password for Synology are not configured in .env file. "
        "Please copy .env.example to .env and fill in your credentials."
    )


# API endpoint paths
AUTH_API_PATH = os.getenv('AUTH_API_PATH', '')      # authentication API path
CAMERA_API_PATH = os.getenv('CAMERA_API_PATH', '')  # camera API path
INFO_API_PATH = os.getenv('INFO_API_PATH', '')      # info query API path

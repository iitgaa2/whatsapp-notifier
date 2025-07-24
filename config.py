"""
Configuration settings for WhatsApp Automation
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
IMAGES_DIR = PROJECT_ROOT / "images"
LOGS_DIR = PROJECT_ROOT / "logs"
MESSAGES_DIR = PROJECT_ROOT / "messages"

# Create directories if they don't exist
IMAGES_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
MESSAGES_DIR.mkdir(exist_ok=True)

# WhatsApp Web settings
WHATSAPP_WEB_URL = "https://web.whatsapp.com"
IMPLICIT_WAIT = 15
PAGE_LOAD_TIMEOUT = 60
QR_SCAN_TIMEOUT = 120

# Message settings
DEFAULT_MESSAGE_FILE = MESSAGES_DIR / "message.txt"
MIN_DELAY_BETWEEN_MESSAGES = 10  # seconds
MAX_DELAY_BETWEEN_MESSAGES = 30  # seconds

# OCR settings
TESSERACT_CONFIG = '--oem 3 --psm 6'
SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']

# Phone number settings
DEFAULT_COUNTRY_CODE = "US"
PHONE_VALIDATION_ENABLED = True

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

# Browser settings
HEADLESS_MODE = False  # Set to True to run in background
CHROME_PROFILE_PATH = None  # Set path to use existing Chrome profile
DOWNLOAD_PATH = PROJECT_ROOT / "downloads"

# Create downloads directory
DOWNLOAD_PATH.mkdir(exist_ok=True)

# User settings (from environment or defaults)
YOUR_PHONE_NUMBER = os.getenv("YOUR_PHONE_NUMBER", "+1 9493102808") 
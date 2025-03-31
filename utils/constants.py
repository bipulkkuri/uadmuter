import os

from dotenv import load_dotenv
from utils.config_reader import read_config, read_config_int, read_config_bool

load_dotenv()
UN_MUTE_WEBHOOK = os.getenv("UN_MUTE_WEBHOOK")
CONFIG_FILE = os.getenv("CONFIG_FILE")
if not CONFIG_FILE:
    raise ValueError("CONFIG_FILE environment variable is not set.")
HOMEASSISTANT_TIMEOUT = read_config_int(
    CONFIG_FILE, "HOMEASSISTANT", "HOMEASSISTANT_TIMEOUT"
)
IMAGE_NAME = read_config(CONFIG_FILE, "CAMERA", "IMAGE_NAME")
CAM_INDEX = read_config_int(CONFIG_FILE, "CAMERA", "CAM_INDEX")
SLEEP_TIME = read_config_int(CONFIG_FILE, "CAMERA", "SLEEP_TIME")
CAM_ENABLED = read_config_bool(CONFIG_FILE, "CAMERA", "ENABLED")
SEARCH_STRING_LIST = read_config(CONFIG_FILE, "CAMERA", "SEARCH_STRING_LIST")

search_string_list = SEARCH_STRING_LIST.split(",")

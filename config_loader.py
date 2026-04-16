import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def get_config():
    """Reads and returns the project configuration from config.json."""
    if not os.path.exists(CONFIG_PATH):
        return {}
    
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[config_loader] Error reading config: {e}")
        return {}

def get_processing_mode():
    config = get_config()
    return config.get("processing", {}).get("default_mode", "regex")

"""Application configuration"""

import os
import json
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CONFIG_FILE = DATA_DIR / "config.json"

# Configuration par défaut
DEFAULT_CONFIG = {
    "window_width": 1200,
    "window_height": 800,
    "theme": "light",
    "elasticsearch_host": "localhost",
    "elasticsearch_port": 9200,
    "elasticsearch_index": "nat_radius_data",
}


class Config:
    """Configuration management"""
    
    @staticmethod
    def load():
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return DEFAULT_CONFIG
        return DEFAULT_CONFIG
    
    @staticmethod
    def save(config_dict):
        """Save configuration to file"""
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")


# Load config on import
config = Config.load()

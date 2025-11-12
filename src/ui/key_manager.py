import json
import os
from datetime import datetime, timedelta
from ui.json_path import resource_path

KEYS_FILE = resource_path("ui//JSON_FILE//keys.json")

class KeyManager:
    @staticmethod
    def load_keys():
        if os.path.exists(KEYS_FILE):
            with open(KEYS_FILE, "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_keys(keys):
        with open(KEYS_FILE, "w") as f:
            json.dump(keys, f)

    @staticmethod
    def validate_key(key):
        keys = KeyManager.load_keys()
        if key in keys:
            expiration_date = datetime.strptime(keys[key], "%Y-%m-%d")
            if datetime.now() < expiration_date:
                return True, expiration_date
        return False, None

    @staticmethod
    def add_key(key, days_valid=30):
        keys = KeyManager.load_keys()
        expiration_date = datetime.now() + timedelta(days=days_valid)
        keys[key] = expiration_date.strftime("%Y-%m-%d")
        KeyManager.save_keys(keys)

    @staticmethod
    def remove_key(key):
        keys = KeyManager.load_keys()
        if key in keys:
            del keys[key]
            KeyManager.save_keys(keys)
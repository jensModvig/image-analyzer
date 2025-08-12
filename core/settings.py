import json
from pathlib import Path

class Settings:
    _instance = None
    _settings = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_settings()
        return cls._instance
    
    def _load_settings(self):
        settings_file = Path.home() / '.image-analyzer-settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                self._settings = json.load(f)
    
    def _save_settings(self):
        settings_file = Path.home() / '.image-analyzer-settings.json'
        with open(settings_file, 'w') as f:
            json.dump(self._settings, f, indent=2)
    
    def get(self, key, default=None):
        return self._settings.get(key, default)
    
    def set(self, key, value):
        self._settings[key] = value
        self._save_settings()
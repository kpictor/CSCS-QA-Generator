import json
import os

class ConfigManager:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """Loads the configuration from the JSON file, or creates a default one."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # Default structure
            return {
                "OPENAI_API_KEY": "",
                "GEMINI_API_KEY": "",
                "LAST_USED_OPENAI_MODEL": "gpt-3.5-turbo",
                "LAST_USED_GEMINI_MODEL": "gemini-1.5-pro-latest"
            }

    def get(self, key, default=None):
        """Gets a value from the configuration."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Sets a value in the configuration."""
        self.config[key] = value

    def save(self):
        """Saves the current configuration to the JSON file."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

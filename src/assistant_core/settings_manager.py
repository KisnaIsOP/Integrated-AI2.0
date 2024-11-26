from typing import Dict, Any, Optional
import json
import os

class SettingsManager:
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            "appearance": {
                "theme": "dark",
                "font_size": 12,
                "font_family": "Helvetica",
                "accent_color": "blue"
            },
            "ai": {
                "default_model": "OpenAI",
                "temperature": 0.7,
                "max_context": 10,
                "stream_responses": True
            },
            "voice": {
                "language": "en-US",
                "energy_threshold": 4000,
                "pause_threshold": 0.8,
                "dynamic_energy": True,
                "auto_calibrate": True
            },
            "system": {
                "startup_apps": [],
                "command_history_size": 100,
                "auto_save": True,
                "save_interval": 300  # seconds
            },
            "notifications": {
                "sound_enabled": True,
                "visual_enabled": True,
                "status_updates": True,
                "error_alerts": True
            }
        }
        self.settings = self.load_settings()
        
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults for any missing settings
                    return self._merge_settings(self.default_settings, settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
        return self.default_settings.copy()
        
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def _merge_settings(self, defaults: Dict, user_settings: Dict) -> Dict:
        """Recursively merge user settings with defaults"""
        result = defaults.copy()
        
        for key, value in user_settings.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
                
        return result
        
    def get_setting(self, category: str, key: str) -> Optional[Any]:
        """Get a specific setting value"""
        try:
            return self.settings[category][key]
        except KeyError:
            return self.default_settings.get(category, {}).get(key)
            
    def update_setting(self, category: str, key: str, value: Any):
        """Update a specific setting"""
        if category not in self.settings:
            self.settings[category] = {}
        self.settings[category][key] = value
        self.save_settings()
        
    def reset_category(self, category: str):
        """Reset a category to default settings"""
        if category in self.default_settings:
            self.settings[category] = self.default_settings[category].copy()
            self.save_settings()
            
    def reset_all(self):
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()
        self.save_settings()
        
    def get_theme(self) -> Dict[str, Any]:
        """Get current theme settings"""
        return {
            "theme": self.get_setting("appearance", "theme"),
            "font_size": self.get_setting("appearance", "font_size"),
            "font_family": self.get_setting("appearance", "font_family"),
            "accent_color": self.get_setting("appearance", "accent_color")
        }
        
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get voice recognition settings"""
        return {
            "language": self.get_setting("voice", "language"),
            "energy_threshold": self.get_setting("voice", "energy_threshold"),
            "pause_threshold": self.get_setting("voice", "pause_threshold"),
            "dynamic_energy": self.get_setting("voice", "dynamic_energy"),
            "auto_calibrate": self.get_setting("voice", "auto_calibrate")
        }
        
    def get_ai_settings(self) -> Dict[str, Any]:
        """Get AI model settings"""
        return {
            "default_model": self.get_setting("ai", "default_model"),
            "temperature": self.get_setting("ai", "temperature"),
            "max_context": self.get_setting("ai", "max_context"),
            "stream_responses": self.get_setting("ai", "stream_responses")
        }
        
    def get_notification_settings(self) -> Dict[str, Any]:
        """Get notification settings"""
        return {
            "sound_enabled": self.get_setting("notifications", "sound_enabled"),
            "visual_enabled": self.get_setting("notifications", "visual_enabled"),
            "status_updates": self.get_setting("notifications", "status_updates"),
            "error_alerts": self.get_setting("notifications", "error_alerts")
        }

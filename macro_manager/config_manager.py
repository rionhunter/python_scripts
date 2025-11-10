"""
Configuration and Settings Manager
Handles application settings, device configurations, and user preferences
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class DeviceConfig:
    """Configuration for an input device"""
    device_id: str
    device_type: str
    enabled: bool = True
    settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data):
        return DeviceConfig(**data)


@dataclass
class TriggerConfig:
    """Configuration for macro triggers"""
    trigger_type: str  # 'hotkey', 'voice', 'midi', 'controller', 'text'
    trigger_data: Dict[str, Any]
    macro_name: str
    enabled: bool = True
    
    def to_dict(self):
        return asdict(self)
    
    @staticmethod
    def from_dict(data):
        return TriggerConfig(**data)


class ConfigManager:
    """Manages all application configuration"""
    
    DEFAULT_SETTINGS = {
        "ui": {
            "theme": "dark",
            "glass_opacity": 0.15,
            "blur_radius": 20,
            "window_width": 1400,
            "window_height": 800,
            "minimize_to_tray": True,
            "start_minimized": False,
        },
        "execution": {
            "typing_speed": 50,  # characters per second
            "mouse_movement_speed": 1.0,  # multiplier
            "execute_in_background": False,
            "confirm_before_execute": False,
            "log_execution": True,
        },
        "input_devices": {
            "keyboard": {
                "enabled": True,
                "capture_all_keys": False,
                "exclusive_mode": False,
            },
            "game_controller": {
                "enabled": False,
                "controller_index": 0,
                "deadzone": 0.1,
            },
            "midi": {
                "enabled": False,
                "device_name": None,
                "channel": 1,
            },
            "voice": {
                "enabled": False,
                "language": "en-US",
                "wake_word": None,
                "continuous_listening": False,
            }
        },
        "ai": {
            "enabled": False,
            "provider": "openai",  # openai, anthropic, local
            "api_key": "",
            "model": "gpt-3.5-turbo",
            "command_interpretation": True,
            "natural_language_macros": True,
        },
        "hotkeys": {
            "show_hide": "ctrl+shift+m",
            "execute_last": "ctrl+shift+e",
            "stop_execution": "ctrl+shift+s",
            "quick_command": "ctrl+shift+space",
        },
        "advanced": {
            "enable_scripting": True,
            "python_path": "python",
            "script_timeout": 30,  # seconds
            "max_macro_actions": 1000,
            "debug_mode": False,
        }
    }
    
    def __init__(self, config_dir: Path = None):
        if config_dir is None:
            config_dir = Path.home() / ".macro_manager"
        
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        
        self.settings_file = self.config_dir / "settings.json"
        self.devices_file = self.config_dir / "devices.json"
        self.triggers_file = self.config_dir / "triggers.json"
        
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.devices: List[DeviceConfig] = []
        self.triggers: List[TriggerConfig] = []
        
        self.load_all()
    
    def load_all(self):
        """Load all configuration files"""
        self.load_settings()
        self.load_devices()
        self.load_triggers()
    
    def save_all(self):
        """Save all configuration files"""
        self.save_settings()
        self.save_devices()
        self.save_triggers()
    
    def load_settings(self):
        """Load application settings"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    self.settings = self._deep_merge(self.DEFAULT_SETTINGS.copy(), loaded)
            except Exception as e:
                print(f"Error loading settings: {e}")
        else:
            self.save_settings()
    
    def save_settings(self):
        """Save application settings"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_devices(self):
        """Load device configurations"""
        if self.devices_file.exists():
            try:
                with open(self.devices_file, 'r') as f:
                    data = json.load(f)
                    self.devices = [DeviceConfig.from_dict(d) for d in data]
            except Exception as e:
                print(f"Error loading devices: {e}")
    
    def save_devices(self):
        """Save device configurations"""
        try:
            with open(self.devices_file, 'w') as f:
                data = [d.to_dict() for d in self.devices]
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving devices: {e}")
    
    def load_triggers(self):
        """Load trigger configurations"""
        if self.triggers_file.exists():
            try:
                with open(self.triggers_file, 'r') as f:
                    data = json.load(f)
                    self.triggers = [TriggerConfig.from_dict(t) for t in data]
            except Exception as e:
                print(f"Error loading triggers: {e}")
    
    def save_triggers(self):
        """Save trigger configurations"""
        try:
            with open(self.triggers_file, 'w') as f:
                data = [t.to_dict() for t in self.triggers]
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving triggers: {e}")
    
    def get(self, key_path: str, default=None):
        """
        Get a setting value by dot-notation path
        Example: get("ui.theme") or get("input_devices.keyboard.enabled")
        """
        keys = key_path.split('.')
        value = self.settings
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Set a setting value by dot-notation path
        Example: set("ui.theme", "light")
        """
        keys = key_path.split('.')
        target = self.settings
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
        self.save_settings()
    
    def add_device(self, device: DeviceConfig):
        """Add a device configuration"""
        # Remove existing device with same ID
        self.devices = [d for d in self.devices if d.device_id != device.device_id]
        self.devices.append(device)
        self.save_devices()
    
    def remove_device(self, device_id: str):
        """Remove a device configuration"""
        self.devices = [d for d in self.devices if d.device_id != device_id]
        self.save_devices()
    
    def get_device(self, device_id: str) -> DeviceConfig:
        """Get device configuration by ID"""
        for device in self.devices:
            if device.device_id == device_id:
                return device
        return None
    
    def add_trigger(self, trigger: TriggerConfig):
        """Add a trigger configuration"""
        self.triggers.append(trigger)
        self.save_triggers()
    
    def remove_trigger(self, macro_name: str, trigger_type: str = None):
        """Remove trigger(s) for a macro"""
        if trigger_type:
            self.triggers = [
                t for t in self.triggers 
                if not (t.macro_name == macro_name and t.trigger_type == trigger_type)
            ]
        else:
            self.triggers = [t for t in self.triggers if t.macro_name != macro_name]
        self.save_triggers()
    
    def get_triggers_for_macro(self, macro_name: str) -> List[TriggerConfig]:
        """Get all triggers for a specific macro"""
        return [t for t in self.triggers if t.macro_name == macro_name]
    
    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()
    
    def export_config(self, filepath: Path):
        """Export all configuration to a single file"""
        export_data = {
            "settings": self.settings,
            "devices": [d.to_dict() for d in self.devices],
            "triggers": [t.to_dict() for t in self.triggers]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def import_config(self, filepath: Path):
        """Import configuration from a file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if "settings" in data:
            self.settings = self._deep_merge(self.DEFAULT_SETTINGS.copy(), data["settings"])
            self.save_settings()
        
        if "devices" in data:
            self.devices = [DeviceConfig.from_dict(d) for d in data["devices"]]
            self.save_devices()
        
        if "triggers" in data:
            self.triggers = [TriggerConfig.from_dict(t) for t in data["triggers"]]
            self.save_triggers()


# Example usage
if __name__ == "__main__":
    config = ConfigManager()
    
    # Test settings
    print("UI Theme:", config.get("ui.theme"))
    print("Typing Speed:", config.get("execution.typing_speed"))
    
    # Change a setting
    config.set("ui.theme", "light")
    print("New Theme:", config.get("ui.theme"))
    
    # Add a device
    device = DeviceConfig(
        device_id="keyboard_1",
        device_type="keyboard",
        enabled=True,
        settings={"capture_all": True}
    )
    config.add_device(device)
    
    # Add a trigger
    trigger = TriggerConfig(
        trigger_type="hotkey",
        trigger_data={"key": "ctrl+alt+p"},
        macro_name="Paste Template",
        enabled=True
    )
    config.add_trigger(trigger)
    
    print(f"\nDevices: {len(config.devices)}")
    print(f"Triggers: {len(config.triggers)}")
    
    # Export config
    export_path = Path("config_backup.json")
    config.export_config(export_path)
    print(f"\nConfiguration exported to {export_path}")

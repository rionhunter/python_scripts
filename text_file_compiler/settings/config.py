"""Settings management for the text file compiler."""

import json
import os
from typing import Dict, Any, Optional

# Try to import PyQt6 QSettings, fall back to JSON-based config
try:
    from PyQt6.QtCore import QSettings
    HAS_PYQT6 = True
except ImportError:
    HAS_PYQT6 = False


class Config:
    """Configuration management for the application."""
    
    def __init__(self):
        self.projects_dir = os.path.join(os.path.expanduser("~"), ".text_file_compiler", "projects")
        self.ensure_directories()
        
        if HAS_PYQT6:
            self.settings = QSettings("TextFileCompiler", "Settings")
        else:
            # Fallback to JSON-based configuration
            self.config_file = os.path.join(os.path.expanduser("~"), ".text_file_compiler", "settings.json")
            self.settings_data = self.load_json_settings()
    
    def load_json_settings(self) -> Dict[str, Any]:
        """Load settings from JSON file (fallback)."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def save_json_settings(self):
        """Save settings to JSON file (fallback)."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings_data, f, indent=2)
        except IOError:
            pass
    
    def get_value(self, key: str, default: Any = None, value_type: type = str) -> Any:
        """Get a configuration value."""
        if HAS_PYQT6:
            return self.settings.value(key, default, type=value_type)
        else:
            keys = key.split('/')
            data = self.settings_data
            for k in keys[:-1]:
                data = data.get(k, {})
                if not isinstance(data, dict):
                    return default
            return data.get(keys[-1], default)
    
    def set_value(self, key: str, value: Any):
        """Set a configuration value."""
        if HAS_PYQT6:
            self.settings.setValue(key, value)
        else:
            keys = key.split('/')
            data = self.settings_data
            for k in keys[:-1]:
                if k not in data:
                    data[k] = {}
                data = data[k]
            data[keys[-1]] = value
            self.save_json_settings()
    
    def ensure_directories(self):
        """Ensure required directories exist."""
        os.makedirs(self.projects_dir, exist_ok=True)
    
    def get_window_geometry(self) -> Dict[str, int]:
        """Get saved window geometry."""
        return {
            'x': self.get_value('window/x', 100, int),
            'y': self.get_value('window/y', 100, int),
            'width': self.get_value('window/width', 1200, int),
            'height': self.get_value('window/height', 800, int)
        }
    
    def set_window_geometry(self, x: int, y: int, width: int, height: int):
        """Save window geometry."""
        self.set_value('window/x', x)
        self.set_value('window/y', y)
        self.set_value('window/width', width)
        self.set_value('window/height', height)
    
    def get_last_directory(self) -> str:
        """Get last used directory."""
        return self.get_value('directories/last_used', os.path.expanduser("~"), str)
    
    def set_last_directory(self, directory: str):
        """Save last used directory."""
        self.set_value('directories/last_used', directory)
    
    def get_current_project(self) -> Optional[str]:
        """Get current project file path."""
        value = self.get_value('project/current', None, str)
        return value if value else None
    
    def set_current_project(self, project_path: Optional[str]):
        """Save current project file path."""
        if project_path:
            self.set_value('project/current', project_path)
        else:
            if HAS_PYQT6:
                self.settings.remove('project/current')
            else:
                keys = 'project/current'.split('/')
                data = self.settings_data
                for k in keys[:-1]:
                    if k in data:
                        data = data[k]
                    else:
                        return
                if keys[-1] in data:
                    del data[keys[-1]]
                self.save_json_settings()
    
    def get_zoom_level(self) -> float:
        """Get zoom level."""
        return self.get_value('ui/zoom', 1.0, float)
    
    def set_zoom_level(self, zoom: float):
        """Save zoom level."""
        self.set_value('ui/zoom', zoom)
    
    def get_scale_factor(self) -> float:
        """Get scale factor."""
        return self.get_value('ui/scale', 1.0, float)
    
    def set_scale_factor(self, scale: float):
        """Save scale factor."""
        self.set_value('ui/scale', scale)


class ProjectConfig:
    """Project-specific configuration."""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.config_data = self.load_project()
    
    def load_project(self) -> Dict[str, Any]:
        """Load project configuration."""
        if os.path.exists(self.project_path):
            try:
                with open(self.project_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return default project structure
        return {
            'name': 'New Project',
            'description': '',
            'files': [],
            'browser_location': os.path.expanduser("~"),
            'output_settings': {
                'include_file_names': True,
                'include_file_tree': True
            }
        }
    
    def save_project(self):
        """Save project configuration."""
        os.makedirs(os.path.dirname(self.project_path), exist_ok=True)
        try:
            with open(self.project_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise RuntimeError(f"Failed to save project: {e}")
    
    def get_name(self) -> str:
        """Get project name."""
        return self.config_data.get('name', 'Untitled Project')
    
    def set_name(self, name: str):
        """Set project name."""
        self.config_data['name'] = name
    
    def get_description(self) -> str:
        """Get project description."""
        return self.config_data.get('description', '')
    
    def set_description(self, description: str):
        """Set project description."""
        self.config_data['description'] = description
    
    def get_files(self) -> list:
        """Get list of files in project."""
        return self.config_data.get('files', [])
    
    def set_files(self, files: list):
        """Set list of files in project."""
        self.config_data['files'] = files
    
    def add_file(self, file_path: str):
        """Add a file to the project."""
        files = self.get_files()
        if file_path not in files:
            files.append(file_path)
            self.set_files(files)
    
    def remove_file(self, file_path: str):
        """Remove a file from the project."""
        files = self.get_files()
        if file_path in files:
            files.remove(file_path)
            self.set_files(files)
    
    def get_browser_location(self) -> str:
        """Get file browser location."""
        return self.config_data.get('browser_location', os.path.expanduser("~"))
    
    def set_browser_location(self, location: str):
        """Set file browser location."""
        self.config_data['browser_location'] = location
    
    def get_output_settings(self) -> Dict[str, Any]:
        """Get output settings."""
        return self.config_data.get('output_settings', {
            'include_file_names': True,
            'include_file_tree': True
        })
    
    def set_output_settings(self, settings: Dict[str, Any]):
        """Set output settings."""
        self.config_data['output_settings'] = settings
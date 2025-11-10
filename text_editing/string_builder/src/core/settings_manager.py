"""
Settings Manager for String Builder Application
Handles application settings, window state persistence, and user preferences.
"""

import json
import os
from typing import Dict, Any, Tuple
from dataclasses import dataclass, asdict

@dataclass
class WindowState:
    """Window state for persistence."""
    x: int = 100
    y: int = 100
    width: int = 1000
    height: int = 700
    is_maximized: bool = False
    zoom_level: float = 1.0

@dataclass
class AppearanceSettings:
    """Appearance settings for the application."""
    theme: str = "frosty_glass"
    primary_color: str = "#8B9D6B"  # Muted green
    secondary_color: str = "#A8B89A"  # Earthy pastel
    background_color: str = "#F5F7F2"  # Light frosty
    text_color: str = "#2C3E2D"  # Dark green
    font_family: str = "Segoe UI"
    font_size: int = 11
    corner_radius: int = 12
    margin_size: int = 20

class SettingsManager:
    """Manages application settings and persistence."""
    
    def __init__(self):
        """Initialize settings manager."""
        self.settings_file = "data/settings.json"
        self.window_state = WindowState()
        self.appearance = AppearanceSettings()
        self.projects_directory = "data/projects"
        self.last_project = None
        self.auto_save = True
        self.backup_frequency = 5  # minutes
        
        # Ensure data directories exist
        os.makedirs("data", exist_ok=True)
        os.makedirs(self.projects_directory, exist_ok=True)
        
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                
                # Load window state
                if 'window_state' in data:
                    ws_data = data['window_state']
                    self.window_state = WindowState(**ws_data)
                
                # Load appearance settings
                if 'appearance' in data:
                    app_data = data['appearance']
                    self.appearance = AppearanceSettings(**app_data)
                
                # Load other settings
                self.last_project = data.get('last_project')
                self.auto_save = data.get('auto_save', True)
                self.backup_frequency = data.get('backup_frequency', 5)
                
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to file."""
        try:
            data = {
                'window_state': asdict(self.window_state),
                'appearance': asdict(self.appearance),
                'last_project': self.last_project,
                'auto_save': self.auto_save,
                'backup_frequency': self.backup_frequency
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def update_window_state(self, x: int, y: int, width: int, height: int, 
                           is_maximized: bool = False, zoom_level: float = None):
        """Update window state."""
        self.window_state.x = x
        self.window_state.y = y
        self.window_state.width = width
        self.window_state.height = height
        self.window_state.is_maximized = is_maximized
        if zoom_level is not None:
            self.window_state.zoom_level = zoom_level
    
    def get_window_geometry(self) -> "QRect":
        """Get window geometry as QRect for PyQt6."""
        try:
            from PyQt6.QtCore import QRect
            return QRect(
                self.window_state.x,
                self.window_state.y,
                self.window_state.width,
                self.window_state.height
            )
        except ImportError:
            return None
    
    def update_appearance(self, **kwargs):
        """Update appearance settings."""
        for key, value in kwargs.items():
            if hasattr(self.appearance, key):
                setattr(self.appearance, key, value)
    
    def get_color_scheme(self) -> Dict[str, str]:
        """Get current color scheme."""
        return {
            'primary': self.appearance.primary_color,
            'secondary': self.appearance.secondary_color,
            'background': self.appearance.background_color,
            'text': self.appearance.text_color
        }
    
    def get_font_config(self) -> Tuple[str, int]:
        """Get font configuration."""
        return (self.appearance.font_family, self.appearance.font_size)

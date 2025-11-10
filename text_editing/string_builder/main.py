"""
String Builder Application
A Python application for building strings with persistent chunks that can be rearranged
using drag and drop functionality, with project management and custom styling.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from typing import Dict, List, Any
from datetime import datetime

from src.ui.main_window import MainWindow
from src.core.project_manager import ProjectManager
from src.core.settings_manager import SettingsManager

class StringBuilderApp:
    """Main application class for the String Builder."""
    
    def __init__(self):
        """Initialize the String Builder application."""
        self.app = QApplication(sys.argv)
        
        # Set application properties
        self.app.setApplicationName("String Builder")
        self.app.setApplicationVersion("1.0")
        self.app.setOrganizationName("String Builder")
        
        # Enable high DPI scaling for PyQt6
        try:
            self.app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        except AttributeError:
            # PyQt6 handles high DPI automatically
            pass
        
        try:
            self.app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            # PyQt6 handles high DPI pixmaps automatically
            pass
        
        # Initialize managers
        self.settings_manager = SettingsManager()
        self.project_manager = ProjectManager(self.settings_manager)
        
        # Create main window
        self.main_window = MainWindow(
            self.project_manager,
            self.settings_manager
        )
        
    def run(self):
        """Start the application."""
        try:
            self.main_window.show()
            return self.app.exec()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return 1
        finally:
            # Save application state before closing
            self.settings_manager.save_settings()
            self.project_manager.save_current_project()

if __name__ == "__main__":
    app = StringBuilderApp()
    sys.exit(app.run())

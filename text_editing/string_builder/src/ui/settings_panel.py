"""
Settings Panel for String Builder Application
Provides UI for configuring application settings and appearance using PyQt6.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTabWidget, QWidget, QScrollArea, QFrame, QLineEdit,
                            QCheckBox, QComboBox, QColorDialog, QMessageBox,
                            QDialogButtonBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from typing import Dict, Any, Callable

class SettingsPanel(QDialog):
    """Settings panel for configuring application preferences."""
    
    def __init__(self, parent, settings_manager, refresh_callback: Callable = None):
        """Initialize settings panel."""
        super().__init__(parent)
        
        self.settings_manager = settings_manager
        self.refresh_callback = refresh_callback
        
        # Temporary settings for preview
        self.temp_settings = {}
        
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 500)
        
        # Center on parent
        if parent:
            parent_geo = parent.geometry()
            self.move(parent_geo.center() - self.rect().center())
        
        self.setup_ui()
        self.load_current_settings()
        self.apply_styling()
    
    def setup_ui(self):
        """Setup the settings UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Application Settings")
        font = QFont(self.settings_manager.appearance.font_family, 16, QFont.Weight.Bold)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_appearance_tab()
        self.create_behavior_tab()
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel | 
            QDialogButtonBox.StandardButton.Apply
        )
        
        button_box.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.save_and_close)
        button_box.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        
        layout.addWidget(button_box)
    
    def create_appearance_tab(self):
        """Create appearance settings tab."""
        tab = QWidget()
        self.tab_widget.addTab(tab, "Appearance")
        
        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll)
        
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        
        # Color scheme section
        self.create_section_header(layout, "Color Scheme")
        
        # Primary color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Primary Color:"))
        self.primary_color_btn = QPushButton()
        self.primary_color_btn.setFixedSize(100, 30)
        self.primary_color_btn.setStyleSheet(f"background-color: {self.settings_manager.appearance.primary_color};")
        self.primary_color_btn.clicked.connect(lambda: self.choose_color("primary_color", self.primary_color_btn))
        color_layout.addWidget(self.primary_color_btn)
        color_layout.addStretch()
        layout.addLayout(color_layout)
        
        # Secondary color
        color_layout2 = QHBoxLayout()
        color_layout2.addWidget(QLabel("Secondary Color:"))
        self.secondary_color_btn = QPushButton()
        self.secondary_color_btn.setFixedSize(100, 30)
        self.secondary_color_btn.setStyleSheet(f"background-color: {self.settings_manager.appearance.secondary_color};")
        self.secondary_color_btn.clicked.connect(lambda: self.choose_color("secondary_color", self.secondary_color_btn))
        color_layout2.addWidget(self.secondary_color_btn)
        color_layout2.addStretch()
        layout.addLayout(color_layout2)
        
        # Font settings section
        self.create_section_header(layout, "Font Settings")
        
        # Font family
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Family:"))
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(["Segoe UI", "Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana"])
        self.font_family_combo.setCurrentText(self.settings_manager.appearance.font_family)
        font_layout.addWidget(self.font_family_combo)
        font_layout.addStretch()
        layout.addLayout(font_layout)
        
        # Font size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Font Size:"))
        self.font_size_edit = QLineEdit(str(self.settings_manager.appearance.font_size))
        self.font_size_edit.setFixedWidth(60)
        size_layout.addWidget(self.font_size_edit)
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        layout.addStretch()
    
    def create_behavior_tab(self):
        """Create behavior settings tab."""
        tab = QWidget()
        self.tab_widget.addTab(tab, "Behavior")
        
        layout = QVBoxLayout(tab)
        
        # Auto-save section
        self.create_section_header(layout, "Auto-Save Settings")
        
        # Auto-save enabled
        self.auto_save_check = QCheckBox("Enable auto-save")
        self.auto_save_check.setChecked(self.settings_manager.auto_save)
        layout.addWidget(self.auto_save_check)
        
        # Auto-save frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Auto-save frequency (minutes):"))
        self.backup_freq_edit = QLineEdit(str(self.settings_manager.backup_frequency))
        self.backup_freq_edit.setFixedWidth(60)
        freq_layout.addWidget(self.backup_freq_edit)
        freq_layout.addStretch()
        layout.addLayout(freq_layout)
        
        layout.addStretch()
    
    def create_section_header(self, layout, text):
        """Create a section header."""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 10, 0, 5)
        
        header_label = QLabel(text)
        font = QFont(self.settings_manager.appearance.font_family, 14, QFont.Weight.Bold)
        header_label.setFont(font)
        header_layout.addWidget(header_label)
        
        layout.addWidget(header_frame)
    
    def choose_color(self, setting_name, button):
        """Open color chooser dialog."""
        current_color = getattr(self.settings_manager.appearance, setting_name)
        color = QColorDialog.getColor(QColor(current_color), self, f"Choose {setting_name.replace('_', ' ').title()}")
        
        if color.isValid():
            color_name = color.name()
            button.setStyleSheet(f"background-color: {color_name};")
            self.temp_settings[setting_name] = color_name
    
    def load_current_settings(self):
        """Load current settings into the form."""
        # Font settings are loaded in create_appearance_tab
        # Clear temp settings
        self.temp_settings = {}
    
    def apply_settings(self):
        """Apply settings without closing dialog."""
        try:
            # Apply appearance settings
            if "primary_color" in self.temp_settings:
                self.settings_manager.appearance.primary_color = self.temp_settings["primary_color"]
            if "secondary_color" in self.temp_settings:
                self.settings_manager.appearance.secondary_color = self.temp_settings["secondary_color"]
            
            # Apply font settings
            self.settings_manager.appearance.font_family = self.font_family_combo.currentText()
            self.settings_manager.appearance.font_size = int(self.font_size_edit.text())
            
            # Apply behavior settings
            self.settings_manager.auto_save = self.auto_save_check.isChecked()
            self.settings_manager.backup_frequency = int(self.backup_freq_edit.text())
            
            # Save settings
            self.settings_manager.save_settings()
            
            # Refresh UI if callback provided
            if self.refresh_callback:
                self.refresh_callback()
            
            QMessageBox.information(self, "Settings", "Settings applied successfully!")
            
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid setting value: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error applying settings: {e}")
    
    def save_and_close(self):
        """Save settings and close dialog."""
        self.apply_settings()
        self.accept()
    
    def apply_styling(self):
        """Apply styling to the dialog."""
        colors = self.settings_manager.get_color_scheme()
        
        self.setStyleSheet(f"""
        QDialog {{
            background-color: {colors['background']};
        }}
        
        QLabel {{
            color: {colors['text']};
        }}
        
        QTabWidget::pane {{
            border: 1px solid {colors['primary']};
            border-radius: 4px;
        }}
        
        QTabBar::tab {{
            background-color: {colors['secondary']};
            color: {colors['text']};
            padding: 8px 16px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QLineEdit, QComboBox {{
            background-color: white;
            border: 1px solid {colors['primary']};
            border-radius: 4px;
            padding: 4px 8px;
            font-family: "{self.settings_manager.appearance.font_family}";
            font-size: {self.settings_manager.appearance.font_size}px;
        }}
        
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors['secondary']};
        }}
        
        QCheckBox {{
            color: {colors['text']};
            font-family: "{self.settings_manager.appearance.font_family}";
            font-size: {self.settings_manager.appearance.font_size}px;
        }}
        """)
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self, 
            "Reset Settings", 
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset appearance settings
            from ..core.settings_manager import AppearanceSettings
            default_appearance = AppearanceSettings()
            
            self.settings_manager.appearance = default_appearance
            
            # Reset behavior settings
            self.settings_manager.auto_save = True
            self.settings_manager.backup_frequency = 5
            
            # Reload form
            self.load_current_settings()
            
            # Update color buttons
            self.primary_color_btn.setStyleSheet(f"background-color: {default_appearance.primary_color};")
            self.secondary_color_btn.setStyleSheet(f"background-color: {default_appearance.secondary_color};")
            
            # Update other fields
            self.font_family_combo.setCurrentText(default_appearance.font_family)
            self.font_size_edit.setText(str(default_appearance.font_size))
            self.auto_save_check.setChecked(True)
            self.backup_freq_edit.setText("5")

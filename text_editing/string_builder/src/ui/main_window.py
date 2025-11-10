"""
Main Window for String Builder Application
Implements frameless window with custom controls and drag-and-drop functionality using PyQt6.
"""

import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect,
                            QMenu, QApplication, QMessageBox)
from PyQt6.QtCore import Qt, QPoint, QRect, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QPainterPath, QAction, QCursor
from typing import Optional, Tuple, Dict, Any
import json

from .chunk_panel import ChunkPanel
from .settings_panel import SettingsPanel
from .project_panel import ProjectPanel

class FramelessWindow(QMainWindow):
    """Base frameless window with custom controls."""
    
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        
        # Window state
        self.is_dragging = False
        self.is_resizing = False
        self.resize_mode = None
        self.drag_start_pos = QPoint()
        self.resize_start_pos = QPoint()
        self.resize_start_geometry = QRect()
        self.zoom_level = 1.0
        
        # Remove window frame
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set window properties
        self.setMinimumSize(600, 400)
        self.setup_window()
    
    def setup_window(self):
        """Setup window appearance and geometry."""
        # Apply saved geometry
        geometry = self.settings_manager.get_window_geometry()
        if geometry:
            self.setGeometry(geometry)
        else:
            self.resize(1000, 700)
            self.center_on_screen()
        
        # Apply transparency
        self.setWindowOpacity(0.95)
        
        # Setup styling
        self.apply_styling()
    
    def center_on_screen(self):
        """Center window on screen."""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def apply_styling(self):
        """Apply frosty glass styling."""
        colors = self.settings_manager.get_color_scheme()
        
        # Create stylesheet
        stylesheet = f"""
        QMainWindow {{
            background-color: {colors['background']};
            border: 2px solid {colors['primary']};
            border-radius: {self.settings_manager.appearance.corner_radius}px;
        }}
        
        QFrame {{
            background-color: {colors['background']};
            border: none;
            border-radius: 8px;
        }}
        
        QLabel {{
            color: {colors['text']};
            background-color: transparent;
            font-family: "{self.settings_manager.appearance.font_family}";
            font-size: {self.settings_manager.appearance.font_size}px;
        }}
        
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-family: "{self.settings_manager.appearance.font_family}";
            font-size: {self.settings_manager.appearance.font_size}px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors['secondary']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary']};
        }}
        """
        
        self.setStyleSheet(stylesheet)
    
    def mousePressEvent(self, event):
        """Handle mouse press events for custom window controls."""
        if event.button() == Qt.MouseButton.RightButton:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                # Shift + Right-click: Center resize
                self.start_center_resize(event.globalPosition().toPoint())
            elif event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
                # Ctrl + Shift + Right-click: Panel resize
                self.start_panel_resize(event.globalPosition().toPoint())
            else:
                # Right-click: Start drag or prepare context menu
                self.start_window_drag(event.globalPosition().toPoint())
        
        elif event.button() == Qt.MouseButton.MiddleButton:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                # Shift + Middle-click: Zoom
                self.start_zoom(event.globalPosition().toPoint())
            elif event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
                # Ctrl + Shift + Middle-click: Scale
                self.start_scale(event.globalPosition().toPoint())
            else:
                # Middle-click: Pan
                self.start_pan(event.globalPosition().toPoint())
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.is_dragging:
            self.perform_window_drag(event.globalPosition().toPoint())
        elif self.is_resizing:
            self.perform_resize(event.globalPosition().toPoint())
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.RightButton:
            if self.is_dragging:
                self.end_window_drag()
            elif not self.is_resizing:
                # Show context menu if no drag occurred
                self.show_context_menu(event.globalPosition().toPoint())
        
        self.is_dragging = False
        self.is_resizing = False
        self.resize_mode = None
        
        super().mouseReleaseEvent(event)
    
    def start_window_drag(self, global_pos):
        """Start window dragging."""
        self.is_dragging = True
        self.drag_start_pos = global_pos - self.pos()
    
    def perform_window_drag(self, global_pos):
        """Perform window dragging."""
        new_pos = global_pos - self.drag_start_pos
        self.move(new_pos)
    
    def end_window_drag(self):
        """End window dragging."""
        self.is_dragging = False
        # Update settings with new position
        self.update_window_state()
    
    def start_center_resize(self, global_pos):
        """Start center resize mode."""
        self.is_resizing = True
        self.resize_mode = "center"
        self.resize_start_pos = global_pos
        self.resize_start_geometry = self.geometry()
    
    def perform_resize(self, global_pos):
        """Perform window resizing."""
        if self.resize_mode == "center":
            # Calculate resize based on mouse movement from center
            center = self.resize_start_geometry.center()
            dx = global_pos.x() - center.x()
            dy = global_pos.y() - center.y()
            
            # Calculate scale factor
            distance = (dx**2 + dy**2)**0.5
            scale_factor = max(0.5, 1.0 + distance / 500)
            
            # Calculate new size
            new_width = int(self.resize_start_geometry.width() * scale_factor)
            new_height = int(self.resize_start_geometry.height() * scale_factor)
            
            # Calculate new position to keep center fixed
            new_x = center.x() - new_width // 2
            new_y = center.y() - new_height // 2
            
            self.setGeometry(new_x, new_y, new_width, new_height)
    
    def start_panel_resize(self, global_pos):
        """Start panel resize mode."""
        # This would resize specific panels under the mouse
        pass
    
    def start_zoom(self, global_pos):
        """Start zoom mode."""
        self.zoom_start_y = global_pos.y()
    
    def start_scale(self, global_pos):
        """Start scale mode."""
        self.scale_start_y = global_pos.y()
    
    def start_pan(self, global_pos):
        """Start pan mode."""
        # This would be used for panning content when zoomed
        pass
    
    def show_context_menu(self, global_pos):
        """Show context menu."""
        if hasattr(self, 'context_menu'):
            self.context_menu.exec(global_pos)
    
    def update_window_state(self):
        """Update window state in settings."""
        geometry = self.geometry()
        self.settings_manager.update_window_state(
            geometry.x(), geometry.y(),
            geometry.width(), geometry.height(),
            self.isMaximized(), self.zoom_level
        )
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.update_window_state()
        super().closeEvent(event)

class MainWindow(FramelessWindow):
    """Main application window with string builder functionality."""
    
    def __init__(self, project_manager, settings_manager):
        """Initialize the main window."""
        self.project_manager = project_manager
        super().__init__(settings_manager)
        
        # UI Components
        self.chunk_panel = None
        self.settings_panel = None
        self.project_panel = None
        self.context_menu = None
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        
        self.setup_ui()
        self.setup_context_menu()
        self.start_auto_save_timer()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Create central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout with margins for the frosty glass effect
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(
            self.settings_manager.appearance.margin_size,
            self.settings_manager.appearance.margin_size,
            self.settings_manager.appearance.margin_size,
            self.settings_manager.appearance.margin_size
        )
        
        # Create content frame with rounded corners
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        main_layout.addWidget(content_frame)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        content_frame.setGraphicsEffect(shadow)
        
        # Content layout
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create header
        self.create_header(content_layout)
        
        # Create project panel
        self.project_panel = ProjectPanel(content_frame, self.project_manager, self.settings_manager)
        content_layout.addWidget(self.project_panel)
        
        # Create chunk panel (main area)
        self.chunk_panel = ChunkPanel(content_frame, self.project_manager, self.settings_manager)
        content_layout.addWidget(self.chunk_panel, 1)  # Give it stretch factor
        
        # Apply initial styling
        self.apply_styling()
    
    def create_header(self, layout):
        """Create window header with title and status."""
        header_frame = QFrame()
        header_frame.setFixedHeight(50)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Title
        title_label = QLabel("String Builder")
        title_font = QFont(self.settings_manager.appearance.font_family, 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Status info
        project_name = "No Project"
        chunk_count = 0
        if self.project_manager.current_project:
            project_name = self.project_manager.current_project.name
            chunk_count = len(self.project_manager.current_project.chunks)
        
        self.status_label = QLabel(f"Project: {project_name} | Chunks: {chunk_count}")
        status_font = QFont(self.settings_manager.appearance.font_family, 10)
        self.status_label.setFont(status_font)
        header_layout.addWidget(self.status_label)
        
        layout.addWidget(header_frame)
    
    def setup_context_menu(self):
        """Setup context menu."""
        self.context_menu = QMenu(self)
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        self.context_menu.addAction(settings_action)
        
        self.context_menu.addSeparator()
        
        # Project actions
        new_project_action = QAction("New Project", self)
        new_project_action.triggered.connect(self.new_project)
        self.context_menu.addAction(new_project_action)
        
        export_action = QAction("Export String", self)
        export_action.triggered.connect(self.export_string)
        self.context_menu.addAction(export_action)
        
        self.context_menu.addSeparator()
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        self.context_menu.addAction(about_action)
        
        self.context_menu.addSeparator()
        
        # Close action
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        self.context_menu.addAction(close_action)
    
    def open_settings(self):
        """Open settings panel."""
        if not self.settings_panel:
            self.settings_panel = SettingsPanel(self, self.settings_manager, self.refresh_ui)
        self.settings_panel.show()
    
    def new_project(self):
        """Create a new project."""
        # This would open a dialog - for now, create a default project
        project = self.project_manager.create_project("New Project")
        self.update_status()
        if self.chunk_panel:
            self.chunk_panel.refresh()
    
    def export_string(self):
        """Export the built string."""
        built_string = self.project_manager.get_built_string()
        
        # Simple message box for now - could be enhanced with a custom dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("Export String")
        msg.setText("Built String:")
        msg.setDetailedText(built_string)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(built_string)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", "String Builder v1.0\nA drag-and-drop string building application")
    
    def update_status(self):
        """Update status label."""
        project_name = "No Project"
        chunk_count = 0
        if self.project_manager.current_project:
            project_name = self.project_manager.current_project.name
            chunk_count = len(self.project_manager.current_project.chunks)
        
        self.status_label.setText(f"Project: {project_name} | Chunks: {chunk_count}")
    
    def refresh_ui(self):
        """Refresh UI after settings change."""
        self.apply_styling()
        if self.chunk_panel:
            self.chunk_panel.refresh()
        if self.project_panel:
            self.project_panel.refresh()
    
    def start_auto_save_timer(self):
        """Start auto-save timer."""
        if self.settings_manager.auto_save:
            interval = self.settings_manager.backup_frequency * 60 * 1000  # Convert to milliseconds
            self.auto_save_timer.start(interval)
    
    def auto_save(self):
        """Perform auto-save."""
        self.project_manager.save_current_project()
        self.settings_manager.save_settings()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save current state
        self.project_manager.save_current_project()
        self.settings_manager.save_settings()
        
        # Stop auto-save timer
        self.auto_save_timer.stop()
        
        super().closeEvent(event)

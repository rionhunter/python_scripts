"""Main GUI window for the PyQt6 text/markdown file compiler."""

import os
import sys
from typing import Optional, List
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QTextEdit, QListWidget, QListWidgetItem, QPushButton,
    QLabel, QLineEdit, QFileDialog, QMessageBox, QTreeWidget, 
    QTreeWidgetItem, QCheckBox, QComboBox, QTabWidget, QProgressBar,
    QMenu, QMenuBar, QStatusBar, QFrame, QScrollArea, QGroupBox
)
from PyQt6.QtCore import (
    Qt, QPoint, QSize, QRect, QTimer, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QThread, pyqtSlot
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QBrush, QLinearGradient,
    QMouseEvent, QWheelEvent, QKeyEvent, QAction, QIcon, QPen,
    QFontMetrics, QResizeEvent
)

from ..core.compiler import Compiler
from ..core.file_processor import FileProcessor
from ..settings.config import Config, ProjectConfig


class GlassFrame(QFrame):
    """Custom frame with frosty glass effect."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(245, 245, 220, 180),
                    stop: 0.5 rgba(240, 248, 255, 160),
                    stop: 1 rgba(250, 240, 230, 180));
                border: 2px solid rgba(34, 139, 34, 120);
                border-radius: 15px;
                margin: 8px;
            }
        """)


class FileBrowser(QTreeWidget):
    """Custom file browser with persistent location."""
    
    fileSelected = pyqtSignal(str)
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.current_directory = self.config.get_last_directory()
        
        self.setHeaderLabels(['Name', 'Size', 'Type'])
        self.setRootIsDecorated(True)
        self.setAlternatingRowColors(True)
        
        # Apply styling
        self.setStyleSheet("""
            QTreeWidget {
                background: rgba(255, 255, 255, 200);
                border: 1px solid rgba(34, 139, 34, 100);
                border-radius: 8px;
                selection-background-color: rgba(34, 139, 34, 100);
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:hover {
                background: rgba(34, 139, 34, 50);
            }
        """)
        
        self.populate_tree()
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
    
    def populate_tree(self):
        """Populate the tree with files and directories."""
        self.clear()
        
        if not os.path.exists(self.current_directory):
            self.current_directory = os.path.expanduser("~")
        
        processor = FileProcessor()
        items = processor.scan_directory(self.current_directory, include_hidden=False)
        
        # Add parent directory item if not at root
        parent_dir = os.path.dirname(self.current_directory)
        if parent_dir != self.current_directory:
            parent_item = QTreeWidgetItem(self)
            parent_item.setText(0, "..")
            parent_item.setText(2, "Directory")
            parent_item.setData(0, Qt.ItemDataRole.UserRole, parent_dir)
            parent_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon))
        
        for item_info in items:
            tree_item = QTreeWidgetItem(self)
            tree_item.setText(0, item_info['name'])
            tree_item.setData(0, Qt.ItemDataRole.UserRole, item_info['path'])
            
            if item_info['is_directory']:
                tree_item.setText(2, "Directory")
                tree_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon))
            else:
                size_str = processor.format_file_size(item_info['size'])
                tree_item.setText(1, size_str)
                tree_item.setText(2, "Text File" if item_info['is_text'] else "Binary File")
                
                icon = (self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon) 
                       if item_info['is_text'] else 
                       self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
                tree_item.setIcon(0, icon)
    
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on tree item."""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        
        if os.path.isdir(path):
            self.current_directory = path
            self.config.set_last_directory(path)
            self.populate_tree()
        else:
            self.fileSelected.emit(path)
    
    def navigate_to(self, directory: str):
        """Navigate to a specific directory."""
        if os.path.isdir(directory):
            self.current_directory = directory
            self.config.set_last_directory(directory)
            self.populate_tree()


class CompilerThread(QThread):
    """Thread for file compilation to avoid blocking UI."""
    
    compilationFinished = pyqtSignal(str)
    compilationError = pyqtSignal(str)
    
    def __init__(self, files: List[str], project_config: dict):
        super().__init__()
        self.files = files
        self.project_config = project_config
        self.compiler = Compiler()
    
    def run(self):
        """Run the compilation in the background."""
        try:
            result = self.compiler.compile_files(self.files, self.project_config)
            self.compilationFinished.emit(result)
        except Exception as e:
            self.compilationError.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window with all enhanced features."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize configuration
        self.config = Config()
        self.current_project_config: Optional[ProjectConfig] = None
        self.compiler = Compiler()
        
        # Window state variables
        self.is_dragging = False
        self.is_resizing = False
        self.drag_start_position = QPoint()
        self.resize_start_position = QPoint()
        self.resize_start_geometry = QRect()
        self.zoom_level = self.config.get_zoom_level()
        self.scale_factor = self.config.get_scale_factor()
        
        # Load current project if exists
        current_project_path = self.config.get_current_project()
        if current_project_path and os.path.exists(current_project_path):
            self.current_project_config = ProjectConfig(current_project_path)
        
        self.init_ui()
        self.setup_styling()
        self.restore_window_geometry()
        self.setup_gradient_outline()
        
        # Apply initial zoom and scale
        self.apply_zoom_and_scale()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Remove window frame for frameless design
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create central widget with glass frame
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Glass container
        self.glass_frame = GlassFrame()
        main_layout.addWidget(self.glass_frame)
        
        # Content layout inside glass frame
        content_layout = QVBoxLayout(self.glass_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title bar
        self.create_title_bar(content_layout)
        
        # Main content area
        self.create_main_content(content_layout)
        
        # Status bar
        self.create_status_bar(content_layout)
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
    
    def create_title_bar(self, layout: QVBoxLayout):
        """Create custom title bar."""
        title_layout = QHBoxLayout()
        
        # Project name
        self.project_label = QLabel("Text File Compiler")
        self.project_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.project_label.setStyleSheet("color: #2e8b57; margin: 5px;")
        title_layout.addWidget(self.project_label)
        
        title_layout.addStretch()
        
        # Window controls
        btn_style = """
            QPushButton {
                background: rgba(34, 139, 34, 100);
                border: none;
                border-radius: 12px;
                color: white;
                font-weight: bold;
                width: 24px;
                height: 24px;
                margin: 2px;
            }
            QPushButton:hover {
                background: rgba(34, 139, 34, 150);
            }
        """
        
        minimize_btn = QPushButton("−")
        minimize_btn.setStyleSheet(btn_style)
        minimize_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(minimize_btn)
        
        close_btn = QPushButton("×")
        close_btn.setStyleSheet(btn_style.replace("34, 139, 34", "220, 20, 60"))
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        layout.addLayout(title_layout)
    
    def create_main_content(self, layout: QVBoxLayout):
        """Create the main content area."""
        # Project controls
        self.create_project_controls(layout)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(main_splitter)
        
        # Left panel: File browser and file list
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel: Output and controls
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
    
    def create_project_controls(self, layout: QVBoxLayout):
        """Create project management controls."""
        project_layout = QHBoxLayout()
        
        # Project dropdown
        self.project_combo = QComboBox()
        self.project_combo.addItem("New Project...")
        self.populate_project_list()
        self.project_combo.currentTextChanged.connect(self.on_project_changed)
        project_layout.addWidget(QLabel("Project:"))
        project_layout.addWidget(self.project_combo)
        
        # Project buttons
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new_project)
        project_layout.addWidget(new_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_project)
        project_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_project)
        project_layout.addWidget(load_btn)
        
        project_layout.addStretch()
        
        layout.addLayout(project_layout)
    
    def create_left_panel(self) -> QWidget:
        """Create the left panel with file browser and list."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Tab widget for browser and files
        tab_widget = QTabWidget()
        left_layout.addWidget(tab_widget)
        
        # File browser tab
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        
        # Browser controls
        browser_controls = QHBoxLayout()
        
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.config.get_last_directory())
        self.path_edit.returnPressed.connect(self.navigate_to_path)
        browser_controls.addWidget(self.path_edit)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        browser_controls.addWidget(browse_btn)
        
        browser_layout.addLayout(browser_controls)
        
        # File browser
        self.file_browser = FileBrowser(self.config)
        self.file_browser.fileSelected.connect(self.add_file_to_project)
        browser_layout.addWidget(self.file_browser)
        
        tab_widget.addTab(browser_widget, "Browse")
        
        # Project files tab
        files_widget = QWidget()
        files_layout = QVBoxLayout(files_widget)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        files_layout.addWidget(self.file_list)
        
        # File controls
        file_controls = QHBoxLayout()
        
        add_file_btn = QPushButton("Add File")
        add_file_btn.clicked.connect(self.add_file_dialog)
        file_controls.addWidget(add_file_btn)
        
        remove_file_btn = QPushButton("Remove")
        remove_file_btn.clicked.connect(self.remove_selected_file)
        file_controls.addWidget(remove_file_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_file_list)
        file_controls.addWidget(clear_btn)
        
        files_layout.addLayout(file_controls)
        
        tab_widget.addTab(files_widget, "Files")
        
        return left_widget
    
    def create_right_panel(self) -> QWidget:
        """Create the right panel with output and controls."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Compilation controls
        compile_layout = QHBoxLayout()
        
        self.include_filenames_cb = QCheckBox("Include file names")
        self.include_filenames_cb.setChecked(True)
        compile_layout.addWidget(self.include_filenames_cb)
        
        self.include_filetree_cb = QCheckBox("Include file tree")
        self.include_filetree_cb.setChecked(True)
        compile_layout.addWidget(self.include_filetree_cb)
        
        compile_layout.addStretch()
        
        compile_btn = QPushButton("Compile")
        compile_btn.clicked.connect(self.compile_files)
        compile_layout.addWidget(compile_btn)
        
        right_layout.addLayout(compile_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)
        
        # Output area
        self.output_text = QTextEdit()
        self.output_text.setFont(QFont("Consolas", 10))
        right_layout.addWidget(self.output_text)
        
        # Output controls
        output_controls = QHBoxLayout()
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        output_controls.addWidget(copy_btn)
        
        save_btn = QPushButton("Save Output")
        save_btn.clicked.connect(self.save_output)
        output_controls.addWidget(save_btn)
        
        clear_output_btn = QPushButton("Clear")
        clear_output_btn.clicked.connect(self.clear_output)
        output_controls.addWidget(clear_output_btn)
        
        right_layout.addLayout(output_controls)
        
        return right_widget
    
    def create_status_bar(self, layout: QVBoxLayout):
        """Create status bar."""
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #2e8b57; margin: 5px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # Zoom controls
        zoom_label = QLabel(f"Zoom: {int(self.zoom_level * 100)}%")
        status_layout.addWidget(zoom_label)
        
        scale_label = QLabel(f"Scale: {int(self.scale_factor * 100)}%")
        status_layout.addWidget(scale_label)
        
        layout.addLayout(status_layout)
    
    def setup_styling(self):
        """Setup the application styling."""
        self.setStyleSheet("""
            QMainWindow {
                background: transparent;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(34, 139, 34, 150),
                    stop: 1 rgba(34, 139, 34, 120));
                border: 1px solid rgba(34, 139, 34, 180);
                border-radius: 8px;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(34, 139, 34, 180),
                    stop: 1 rgba(34, 139, 34, 150));
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(34, 139, 34, 120),
                    stop: 1 rgba(34, 139, 34, 180));
            }
            QTextEdit, QListWidget {
                background: rgba(255, 255, 255, 220);
                border: 1px solid rgba(34, 139, 34, 100);
                border-radius: 8px;
                padding: 8px;
            }
            QLineEdit, QComboBox {
                background: rgba(255, 255, 255, 200);
                border: 1px solid rgba(34, 139, 34, 100);
                border-radius: 6px;
                padding: 4px 8px;
            }
            QTabWidget::pane {
                border: 1px solid rgba(34, 139, 34, 100);
                border-radius: 8px;
            }
            QTabBar::tab {
                background: rgba(34, 139, 34, 100);
                color: white;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: rgba(34, 139, 34, 150);
            }
        """)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Escape to close
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def setup_gradient_outline(self):
        """Setup gradient outline that reacts to window position."""
        # This will be updated in paintEvent
        pass
    
    def restore_window_geometry(self):
        """Restore window geometry from settings."""
        geometry = self.config.get_window_geometry()
        self.setGeometry(geometry['x'], geometry['y'], geometry['width'], geometry['height'])
    
    def save_window_geometry(self):
        """Save current window geometry."""
        geometry = self.geometry()
        self.config.set_window_geometry(geometry.x(), geometry.y(), geometry.width(), geometry.height())
    
    def apply_zoom_and_scale(self):
        """Apply current zoom and scale settings."""
        font = self.font()
        base_size = 10
        font.setPointSize(max(8, int(base_size * self.zoom_level)))
        self.setFont(font)
        
        # Scale the entire window
        transform_origin = self.rect().center()
        # Note: Window scaling would require more complex implementation
    
    # Mouse event handlers for custom window behavior
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.RightButton:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                # Resize from center
                self.is_resizing = True
                self.resize_start_position = event.globalPosition().toPoint()
                self.resize_start_geometry = self.geometry()
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                # Start drag or show context menu
                self.drag_start_position = event.globalPosition().toPoint()
                self.is_dragging = True
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        if self.is_dragging and event.buttons() == Qt.MouseButton.RightButton:
            # Move window
            delta = event.globalPosition().toPoint() - self.drag_start_position
            self.move(self.pos() + delta)
            self.drag_start_position = event.globalPosition().toPoint()
        
        elif self.is_resizing and event.buttons() == Qt.MouseButton.RightButton:
            # Resize window from center
            delta = event.globalPosition().toPoint() - self.resize_start_position
            
            center = self.resize_start_geometry.center()
            new_width = max(400, self.resize_start_geometry.width() + delta.x() * 2)
            new_height = max(300, self.resize_start_geometry.height() + delta.y() * 2)
            
            new_rect = QRect(
                center.x() - new_width // 2,
                center.y() - new_height // 2,
                new_width,
                new_height
            )
            self.setGeometry(new_rect)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.RightButton:
            if self.is_dragging and not self.is_resizing:
                # Check if we actually dragged or just clicked
                if (event.globalPosition().toPoint() - self.drag_start_position).manhattanLength() < 5:
                    self.show_context_menu(event.pos())
            
            self.is_dragging = False
            self.is_resizing = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle wheel events for zoom and scale."""
        modifiers = event.modifiers()
        
        if modifiers == Qt.KeyboardModifier.ShiftModifier and event.buttons() == Qt.MouseButton.MiddleButton:
            # Zoom in/out
            delta = event.angleDelta().y() / 1200.0
            self.zoom_level = max(0.5, min(3.0, self.zoom_level + delta))
            self.config.set_zoom_level(self.zoom_level)
            self.apply_zoom_and_scale()
            
        elif modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier) and event.buttons() == Qt.MouseButton.MiddleButton:
            # Scale window and contents
            delta = event.angleDelta().y() / 1200.0
            self.scale_factor = max(0.5, min(2.0, self.scale_factor + delta))
            self.config.set_scale_factor(self.scale_factor)
            self.apply_zoom_and_scale()
        
        elif event.buttons() == Qt.MouseButton.MiddleButton:
            # Pan (when zoomed) - would require scroll area implementation
            pass
        
        super().wheelEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle close event."""
        self.save_window_geometry()
        if self.current_project_config:
            self.save_project()
        event.accept()
    
    def show_context_menu(self, position: QPoint):
        """Show context menu."""
        menu = QMenu(self)
        
        # Project actions
        new_action = QAction("New Project", self)
        new_action.triggered.connect(self.new_project)
        menu.addAction(new_action)
        
        save_action = QAction("Save Project", self)
        save_action.triggered.connect(self.save_project)
        menu.addAction(save_action)
        
        load_action = QAction("Load Project", self)
        load_action.triggered.connect(self.load_project)
        menu.addAction(load_action)
        
        menu.addSeparator()
        
        # View actions
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(lambda: self.adjust_zoom(0.1))
        menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(lambda: self.adjust_zoom(-0.1))
        menu.addAction(zoom_out_action)
        
        menu.addSeparator()
        
        # Window actions
        minimize_action = QAction("Minimize", self)
        minimize_action.triggered.connect(self.showMinimized)
        menu.addAction(minimize_action)
        
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def adjust_zoom(self, delta: float):
        """Adjust zoom level."""
        self.zoom_level = max(0.5, min(3.0, self.zoom_level + delta))
        self.config.set_zoom_level(self.zoom_level)
        self.apply_zoom_and_scale()
    
    # Project management methods
    def populate_project_list(self):
        """Populate the project dropdown."""
        # This would scan for .json project files in the projects directory
        pass
    
    def new_project(self):
        """Create a new project."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save New Project", 
            os.path.join(self.config.projects_dir, "new_project.json"),
            "Project Files (*.json)"
        )
        
        if file_path:
            self.current_project_config = ProjectConfig(file_path)
            self.current_project_config.save_project()
            self.config.set_current_project(file_path)
            self.project_label.setText(f"Project: {self.current_project_config.get_name()}")
            self.load_project_files()
    
    def save_project(self):
        """Save current project."""
        if self.current_project_config:
            # Update project with current files
            files = []
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                files.append(item.data(Qt.ItemDataRole.UserRole))
            
            self.current_project_config.set_files(files)
            self.current_project_config.set_output_settings({
                'include_file_names': self.include_filenames_cb.isChecked(),
                'include_file_tree': self.include_filetree_cb.isChecked()
            })
            
            try:
                self.current_project_config.save_project()
                self.status_label.setText("Project saved")
                QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project: {e}")
    
    def load_project(self):
        """Load an existing project."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Project", 
            self.config.projects_dir,
            "Project Files (*.json)"
        )
        
        if file_path:
            try:
                self.current_project_config = ProjectConfig(file_path)
                self.config.set_current_project(file_path)
                self.project_label.setText(f"Project: {self.current_project_config.get_name()}")
                self.load_project_files()
                
                # Update browser location
                browser_location = self.current_project_config.get_browser_location()
                self.file_browser.navigate_to(browser_location)
                self.path_edit.setText(browser_location)
                
                # Update output settings
                output_settings = self.current_project_config.get_output_settings()
                self.include_filenames_cb.setChecked(output_settings.get('include_file_names', True))
                self.include_filetree_cb.setChecked(output_settings.get('include_file_tree', True))
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {e}")
    
    def load_project_files(self):
        """Load files from current project into the list."""
        if not self.current_project_config:
            return
        
        self.file_list.clear()
        for file_path in self.current_project_config.get_files():
            self.add_file_to_list(file_path)
    
    def on_project_changed(self, project_name: str):
        """Handle project selection change."""
        # This would be implemented when project dropdown is fully functional
        pass
    
    # File management methods
    def add_file_to_project(self, file_path: str):
        """Add a file to the current project."""
        if not os.path.exists(file_path):
            return
        
        # Check if file is already in the list
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == file_path:
                return
        
        self.add_file_to_list(file_path)
        
        # Add to project config
        if self.current_project_config:
            self.current_project_config.add_file(file_path)
    
    def add_file_to_list(self, file_path: str):
        """Add a file to the file list widget."""
        item = QListWidgetItem(os.path.basename(file_path))
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        item.setToolTip(file_path)
        
        # Set icon based on file type
        if FileProcessor.is_text_file(file_path):
            item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
        else:
            item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        self.file_list.addItem(item)
    
    def add_file_dialog(self):
        """Show file selection dialog."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Files", 
            self.config.get_last_directory(),
            "All Files (*)"
        )
        
        for file_path in files:
            self.add_file_to_project(file_path)
    
    def remove_selected_file(self):
        """Remove selected file from the list."""
        current_item = self.file_list.currentItem()
        if current_item:
            file_path = current_item.data(Qt.ItemDataRole.UserRole)
            
            # Remove from project config
            if self.current_project_config:
                self.current_project_config.remove_file(file_path)
            
            # Remove from list
            row = self.file_list.row(current_item)
            self.file_list.takeItem(row)
    
    def clear_file_list(self):
        """Clear all files from the list."""
        self.file_list.clear()
        if self.current_project_config:
            self.current_project_config.set_files([])
    
    # Browser methods
    def navigate_to_path(self):
        """Navigate to the path in the path edit."""
        path = self.path_edit.text()
        if os.path.isdir(path):
            self.file_browser.navigate_to(path)
            
            # Update project browser location
            if self.current_project_config:
                self.current_project_config.set_browser_location(path)
    
    def browse_directory(self):
        """Show directory browser dialog."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", 
            self.path_edit.text()
        )
        
        if directory:
            self.path_edit.setText(directory)
            self.file_browser.navigate_to(directory)
            
            # Update project browser location
            if self.current_project_config:
                self.current_project_config.set_browser_location(directory)
    
    # Compilation methods
    def compile_files(self):
        """Compile the selected files."""
        files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            files.append(item.data(Qt.ItemDataRole.UserRole))
        
        if not files:
            QMessageBox.warning(self, "Warning", "No files selected for compilation.")
            return
        
        # Prepare project config for compilation
        project_config = {
            'name': self.current_project_config.get_name() if self.current_project_config else "Untitled Project",
            'description': self.current_project_config.get_description() if self.current_project_config else "",
            'output_settings': {
                'include_file_names': self.include_filenames_cb.isChecked(),
                'include_file_tree': self.include_filetree_cb.isChecked()
            }
        }
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start compilation in background thread
        self.compiler_thread = CompilerThread(files, project_config)
        self.compiler_thread.compilationFinished.connect(self.on_compilation_finished)
        self.compiler_thread.compilationError.connect(self.on_compilation_error)
        self.compiler_thread.start()
        
        self.status_label.setText("Compiling files...")
    
    @pyqtSlot(str)
    def on_compilation_finished(self, result: str):
        """Handle compilation completion."""
        self.progress_bar.setVisible(False)
        self.output_text.setPlainText(result)
        self.status_label.setText("Compilation completed")
        QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
    
    @pyqtSlot(str)
    def on_compilation_error(self, error: str):
        """Handle compilation error."""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Compilation Error", f"Failed to compile files:\n{error}")
        self.status_label.setText("Compilation failed")
        QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
    
    # Output methods
    def copy_to_clipboard(self):
        """Copy output to clipboard."""
        text = self.output_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.status_label.setText("Copied to clipboard")
            QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
    
    def save_output(self):
        """Save output to file."""
        text = self.output_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "Warning", "No output to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Output", 
            "compiled_output.md",
            "Markdown Files (*.md);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                self.status_label.setText(f"Output saved to {os.path.basename(file_path)}")
                QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save output:\n{e}")
    
    def clear_output(self):
        """Clear the output area."""
        self.output_text.clear()
    
    def paintEvent(self, event):
        """Custom paint event for gradient outline."""
        super().paintEvent(event)
        
        # Create gradient outline that reacts to window position
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate opacity based on screen position
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_center = self.geometry().center()
        
        # Distance from screen center affects opacity
        screen_center = screen_geometry.center()
        distance = ((window_center.x() - screen_center.x()) ** 2 + 
                   (window_center.y() - screen_center.y()) ** 2) ** 0.5
        max_distance = (screen_geometry.width() ** 2 + screen_geometry.height() ** 2) ** 0.5
        opacity = max(50, int(255 - (distance / max_distance) * 205))
        
        # Create gradient
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(34, 139, 34, opacity))
        gradient.setColorAt(0.5, QColor(60, 179, 113, opacity // 2))
        gradient.setColorAt(1, QColor(34, 139, 34, opacity))
        
        # Draw outline
        pen = QPen(QBrush(gradient), 3)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 15, 15)
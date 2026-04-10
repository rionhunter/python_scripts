"""Main GUI window for the PyQt6 text/markdown file compiler."""

import os
import sys
import math
from functools import partial
from typing import Optional, List, Iterable
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QTextEdit, QListWidget, QListWidgetItem, QPushButton,
    QLabel, QLineEdit, QFileDialog, QMessageBox, QTreeWidget, 
    QTreeWidgetItem, QCheckBox, QComboBox, QTabWidget, QProgressBar,
    QMenu, QMenuBar, QStatusBar, QFrame, QScrollArea, QGroupBox,
    QInputDialog, QDialog, QDialogButtonBox, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QPoint, QSize, QRect, QTimer, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QThread, pyqtSlot
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QPixmap, QPainter, QBrush, QLinearGradient,
    QMouseEvent, QWheelEvent, QKeyEvent, QAction, QIcon, QPen,
    QShortcut, QKeySequence,
    QFontMetrics, QResizeEvent
)

try:
    from ..core.compiler import Compiler
    from ..core.file_processor import FileProcessor
    from ..settings.config import Config, ProjectConfig
except ImportError:
    from core.compiler import Compiler
    from core.file_processor import FileProcessor
    from settings.config import Config, ProjectConfig


class GlassFrame(QFrame):
    """Custom frame with frosty glass effect."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(245, 245, 220, 230),
                    stop: 0.5 rgba(240, 248, 255, 220),
                    stop: 1 rgba(250, 240, 230, 230));
                border: 2px solid rgba(34, 139, 34, 180);
                border-radius: 15px;
                margin: 8px;
            }
        """)


class SlimTreeCard(QWidget):
    """Slim tree row card used for both files and directories."""

    checkedChanged = pyqtSignal(bool)
    expandRequested = pyqtSignal(bool)

    def __init__(self, title: str, subtitle: str, is_directory: bool, parent=None):
        super().__init__(parent)
        self.is_directory = is_directory

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        if is_directory:
            self.expand_button = QPushButton("▾")
            self.expand_button.setFixedSize(18, 18)
            self.expand_button.setCheckable(True)
            self.expand_button.setChecked(True)
            self.expand_button.clicked.connect(self.expandRequested.emit)
            layout.addWidget(self.expand_button)
        else:
            self.expand_button = None
            spacer = QWidget()
            spacer.setFixedWidth(18)
            layout.addWidget(spacer)

        self.checkbox = QCheckBox()
        self.checkbox.setTristate(is_directory)
        self.checkbox.stateChanged.connect(lambda state: self.checkedChanged.emit(state == Qt.CheckState.Checked))
        layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignTop)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(0)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: 700; color: rgba(34, 68, 34, 230);")
        text_column.addWidget(self.title_label)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet("color: rgba(60, 70, 60, 180); font-size: 9pt;")
        text_column.addWidget(self.subtitle_label)
        layout.addLayout(text_column, 1)

        badge = QLabel("DIR" if is_directory else "FILE")
        badge.setStyleSheet(
            "background: rgba(34, 139, 34, 40);"
            "border: 1px solid rgba(34, 139, 34, 80);"
            "border-radius: 8px;"
            "padding: 2px 6px;"
            "font-size: 8pt;"
            "font-weight: 700;"
            "color: rgba(34, 90, 34, 220);"
        )
        layout.addWidget(badge, alignment=Qt.AlignmentFlag.AlignTop)

        self.setStyleSheet("""
            SlimTreeCard {
                background: rgba(255, 255, 255, 210);
                border: 1px solid rgba(34, 139, 34, 70);
                border-radius: 10px;
            }
            SlimTreeCard:hover {
                background: rgba(248, 252, 248, 230);
                border: 1px solid rgba(34, 139, 34, 110);
            }
            SlimTreeCard QPushButton {
                background: rgba(34, 139, 34, 20);
                color: rgba(34, 90, 34, 220);
                border: 1px solid rgba(34, 139, 34, 60);
                border-radius: 6px;
                padding: 0;
                font-weight: 700;
            }
            SlimTreeCard QPushButton:hover {
                background: rgba(34, 139, 34, 40);
            }
            SlimTreeCard QCheckBox::indicator {
                width: 14px;
                height: 14px;
            }
        """)

    def set_check_state(self, state: Qt.CheckState):
        """Update checkbox state without emitting user-facing signals."""
        previous = self.checkbox.blockSignals(True)
        self.checkbox.setCheckState(state)
        self.checkbox.blockSignals(previous)

    def set_expanded(self, expanded: bool):
        """Update the expansion affordance."""
        if not self.expand_button:
            return
        previous = self.expand_button.blockSignals(True)
        self.expand_button.setChecked(expanded)
        self.expand_button.setText("▾" if expanded else "▸")
        self.expand_button.blockSignals(previous)

    def set_check_enabled(self, enabled: bool):
        """Enable or disable checkbox interactions."""
        self.checkbox.setEnabled(enabled)


class FileBrowser(QTreeWidget):
    """Checkbox-driven project tree with expandable directory cards."""

    selectionToggled = pyqtSignal(str, bool, bool)
    directoryChanged = pyqtSignal(str)

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.current_directory = self.config.get_last_directory()
        self._path_to_item: dict[str, QTreeWidgetItem] = {}
        self._path_to_card: dict[str, SlimTreeCard] = {}
        self._syncing_selection = False

        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.setIndentation(18)
        self.setUniformRowHeights(False)
        self.setAnimated(True)
        self.setStyleSheet("""
            QTreeWidget {
                background: rgba(255, 255, 255, 180);
                border: 1px solid rgba(34, 139, 34, 100);
                border-radius: 12px;
                padding: 6px;
            }
            QTreeWidget::item {
                border: none;
                padding: 2px 0;
            }
        """)

        self.itemExpanded.connect(self._on_item_expanded)
        self.itemCollapsed.connect(self._on_item_collapsed)
        # Defer populating the tree in test environments to avoid scanning
        # the user's home directory during unit tests (slow/fragile).
        try:
            # Avoid heavy directory scanning during automated or headless runs
            skip_populate = bool(os.environ.get('PYTEST_CURRENT_TEST')) or os.environ.get('QT_QPA_PLATFORM') == 'offscreen'
            if not skip_populate:
                # Schedule population after the event loop starts to avoid blocking UI initialization
                try:
                    QTimer.singleShot(0, lambda: self.populate_tree(False))
                except Exception:
                    # Fall back to immediate populate if QTimer isn't available
                    self.populate_tree(False)
        except Exception:
            # If environment inspect fails, populate by default
            self.populate_tree()

    def populate_tree(self, recursive: bool = True):
        """Rebuild the tree from the current root directory."""
        self.clear()
        self._path_to_item.clear()
        self._path_to_card.clear()

        if not os.path.isdir(self.current_directory):
            self.current_directory = os.path.expanduser("~")

        root_name = os.path.basename(self.current_directory.rstrip(os.sep)) or self.current_directory
        root_item = self._create_item(None, self.current_directory, True, root_name, self.current_directory)
        root_item.setExpanded(True)
        # Populate either just immediate children (fast) or full recursive tree.
        if recursive:
            # Full recursive population (existing behavior)
            self._populate_children(root_item, self.current_directory)
            self._update_directory_states(root_item)
            self.expandItem(root_item)
            return

        try:
            for item_info in FileProcessor.scan_directory(self.current_directory, include_hidden=False):
                path = item_info['path']
                is_dir = item_info['is_directory']
                name = item_info['name']
                subtitle = '' if is_dir else FileProcessor.format_file_size(item_info.get('size', 0))
                child = self._create_item(root_item, path, is_dir, name, subtitle)
                # For directories, leave collapsed and don't recurse until user expands.
                if is_dir:
                    child.setExpanded(False)

            # Update tri-state for root based on immediate children
            self._update_directory_states(root_item)
            self.expandItem(root_item)
        except Exception:
            # Fall back to full population if scan fails
            self._populate_children(root_item, self.current_directory)
            self._update_directory_states(root_item)
            self.expandItem(root_item)

    def _populate_children(self, parent_item: QTreeWidgetItem, directory: str):
        """Populate children under a directory node."""
        for item_info in FileProcessor.scan_directory(directory, include_hidden=False):
            path = item_info['path']
            if item_info['is_directory']:
                # For directories, show a local relative path (relative to the tree root)
                try:
                    rel = os.path.relpath(path, self.current_directory)
                except Exception:
                    rel = path
                subtitle = rel if rel != '.' else ''
                child_item = self._create_item(parent_item, path, True, item_info['name'], subtitle)
                self._populate_children(child_item, path)
                has_children = child_item.childCount() > 0
                card = self._path_to_card[path]
                card.set_check_enabled(has_children)
                if not has_children:
                    card.subtitle_label.setText("No text files")
                    card.set_expanded(False)
                child_item.setExpanded(False)
                continue

            if not item_info['is_text']:
                continue

            # For files, display only the human-readable size (avoid full file paths in tree)
            size_str = FileProcessor.format_file_size(item_info['size'])
            subtitle = f"{size_str}"
            self._create_item(parent_item, path, False, item_info['name'], subtitle)

    def _create_item(
        self,
        parent: Optional[QTreeWidgetItem],
        path: str,
        is_directory: bool,
        title: str,
        subtitle: str,
    ) -> QTreeWidgetItem:
        """Create a tree item backed by a slim card widget."""
        item = QTreeWidgetItem(parent or self)
        item.setData(0, Qt.ItemDataRole.UserRole, path)
        item.setData(0, Qt.ItemDataRole.UserRole + 1, is_directory)
        item.setSizeHint(0, QSize(0, 42 if is_directory else 38))

        card = SlimTreeCard(title, subtitle, is_directory, self)
        card.checkedChanged.connect(partial(self._on_card_checked_changed, path, is_directory))
        if is_directory:
            card.expandRequested.connect(partial(self._on_expand_requested, path))

        self.setItemWidget(item, 0, card)
        self._path_to_item[path] = item
        self._path_to_card[path] = card
        return item

    def _on_card_checked_changed(self, path: str, is_directory: bool, checked: bool):
        """Relay user-triggered checkbox changes."""
        if self._syncing_selection:
            return
        self.selectionToggled.emit(path, is_directory, checked)

    def _on_expand_requested(self, path: str, expanded: bool):
        """Expand or collapse a directory row from its custom button."""
        item = self._path_to_item.get(path)
        if not item:
            return
        item.setExpanded(expanded)

    def _on_item_expanded(self, item: QTreeWidgetItem):
        """Keep directory card state aligned with tree state."""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        card = self._path_to_card.get(path)
        if card:
            card.set_expanded(True)

    def _on_item_collapsed(self, item: QTreeWidgetItem):
        """Keep directory card state aligned with tree state."""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        card = self._path_to_card.get(path)
        if card:
            card.set_expanded(False)

    def set_selected_files(self, selected_files: Iterable[str]):
        """Sync file and directory checkbox states to the ordered project file list."""
        selected = set(selected_files)
        self._syncing_selection = True
        try:
            for path, item in self._path_to_item.items():
                is_directory = bool(item.data(0, Qt.ItemDataRole.UserRole + 1))
                card = self._path_to_card[path]
                if is_directory:
                    continue
                state = Qt.CheckState.Checked if path in selected else Qt.CheckState.Unchecked
                card.set_check_state(state)

            root_item = self.topLevelItem(0)
            if root_item:
                self._update_directory_states(root_item)
        finally:
            self._syncing_selection = False

    def _update_directory_states(self, item: QTreeWidgetItem) -> Qt.CheckState:
        """Recalculate tri-state directory checkboxes from their descendants."""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        is_directory = bool(item.data(0, Qt.ItemDataRole.UserRole + 1))
        card = self._path_to_card[path]

        if not is_directory:
            return card.checkbox.checkState()

        child_states: List[Qt.CheckState] = []
        for index in range(item.childCount()):
            child_states.append(self._update_directory_states(item.child(index)))

        if not child_states:
            card.set_check_state(Qt.CheckState.Unchecked)
            return Qt.CheckState.Unchecked

        if any(state == Qt.CheckState.PartiallyChecked for state in child_states):
            state = Qt.CheckState.PartiallyChecked
        elif all(state == Qt.CheckState.Checked for state in child_states):
            state = Qt.CheckState.Checked
        elif all(state == Qt.CheckState.Unchecked for state in child_states):
            state = Qt.CheckState.Unchecked
        else:
            state = Qt.CheckState.PartiallyChecked

        card.set_check_state(state)
        return state

    def navigate_to(self, directory: str):
        """Navigate to a specific directory root."""
        if not os.path.isdir(directory):
            return
        self.current_directory = directory
        self.config.set_last_directory(directory)
        self.populate_tree()
        self.directoryChanged.emit(directory)


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
        self.project_files: List[str] = []
        self.project_name_letters: List[QLabel] = []
        self.project_name_tick = 0
        self.auto_populate_enabled = self.config.get_auto_populate_enabled()
        self.exclude_empty_enabled = self.config.get_exclude_empty_enabled()
        self.include_file_names_enabled = self.config.get_include_file_names_enabled()
        self.include_file_tree_enabled = self.config.get_include_file_tree_enabled()
        self.include_subdirectories_enabled = self.config.get_include_subdirectories_enabled()

        self.right_drag_press_position = QPoint()
        self.right_drag_moved = False
        self.suppress_context_menu_release = False

        self.drag_motion_intensity = 0.0
        self.drag_motion_direction = 1
        
        # Load current project if exists
        current_project_path = self.config.get_current_project()
        if current_project_path and os.path.exists(current_project_path):
            self.current_project_config = ProjectConfig(current_project_path)
        
        # Initialize UI and styling (instrumented for debugging test hang)
        print('MainWindow: calling init_ui()')
        self.init_ui()
        print('MainWindow: returned from init_ui()')

        print('MainWindow: calling setup_styling()')
        self.setup_styling()
        print('MainWindow: returned from setup_styling()')

        print('MainWindow: calling restore_window_geometry()')
        self.restore_window_geometry()
        print('MainWindow: returned from restore_window_geometry()')

        print('MainWindow: calling setup_gradient_outline()')
        self.setup_gradient_outline()
        print('MainWindow: returned from setup_gradient_outline()')

        # Apply initial zoom and scale
        print('MainWindow: calling apply_zoom_and_scale()')
        self.apply_zoom_and_scale()
        print('MainWindow: returned from apply_zoom_and_scale()')
    
    def init_ui(self):
        """Initialize the user interface."""
        # Remove window frame for frameless design
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create central widget with glass frame
        central_widget = QWidget()
        central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Glass container
        self.glass_frame = GlassFrame()
        self.glass_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.glass_frame)
        
        # Content layout inside glass frame
        content_layout = QVBoxLayout(self.glass_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)

        print('init_ui: calling create_project_name_banner()')
        self.create_project_name_banner(main_layout)
        print('init_ui: returned from create_project_name_banner()')
        # Ensure the project name banner stays compact and the glass frame takes remaining space
        try:
            main_layout.setStretch(0, 0)
            main_layout.setStretch(1, 1)
        except Exception:
            pass
        
        # Title bar
        print('init_ui: calling create_title_bar()')
        self.create_title_bar(content_layout)
        print('init_ui: returned from create_title_bar()')
        
        # Main content area
        print('init_ui: calling create_main_content()')
        self.create_main_content(content_layout)
        print('init_ui: returned from create_main_content()')
        
        # Status bar
        print('init_ui: calling create_status_bar()')
        self.create_status_bar(content_layout)
        print('init_ui: returned from create_status_bar()')
        
        # Setup keyboard shortcuts
        print('init_ui: calling setup_shortcuts()')
        self.setup_shortcuts()
        print('init_ui: returned from setup_shortcuts()')

    def create_project_name_banner(self, main_layout: QVBoxLayout):
        """Create floating project name banner above the glass frame."""
        self.project_name_container = QWidget()
        # Keep banner compact to maximize usable workspace
        self.project_name_container.setFixedHeight(28)
        banner_layout = QHBoxLayout(self.project_name_container)
        banner_layout.setContentsMargins(0, 0, 0, 0)

        self.project_name_row = QWidget()
        self.project_name_row.setStyleSheet("background: transparent;")
        self.project_name_row_layout = QHBoxLayout(self.project_name_row)
        self.project_name_row_layout.setContentsMargins(10, 2, 10, 2)
        self.project_name_row_layout.setSpacing(0)
        self.project_name_row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        banner_layout.addWidget(self.project_name_row, alignment=Qt.AlignmentFlag.AlignLeft)
        banner_layout.addStretch(1)
        main_layout.insertWidget(0, self.project_name_container)

        # Avoid starting the animation timer when running under pytest
        # (timers/paint events can interfere with headless test runners).
        self.project_name_timer = None
        try:
            if not os.environ.get('PYTEST_CURRENT_TEST'):
                self.project_name_timer = QTimer(self)
                self.project_name_timer.timeout.connect(self.animate_project_name)
                self.project_name_timer.start(45)
        except Exception:
            # In environments where QTimer cannot be started, skip animation
            self.project_name_timer = None

        initial_name = "New Project"
        if self.current_project_config:
            initial_name = self.current_project_config.get_name()
        self.set_project_name_display(initial_name)

    def set_project_name_display(self, project_name: str):
        """Set floating project name letters used by flourish animation."""
        if not project_name:
            project_name = "Untitled Project"

        while self.project_name_row_layout.count():
            child = self.project_name_row_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.project_name_letters = []
        for letter in project_name:
            label = QLabel(letter)
            label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            label.setStyleSheet("color: rgba(46, 139, 87, 230); background: transparent;")
            self.project_name_row_layout.addWidget(label)
            self.project_name_letters.append(label)

    def animate_project_name(self):
        """Animate project name letters with drag-driven trailing motion."""
        if not self.project_name_letters:
            return

        self.project_name_tick += 1

        if not self.is_dragging:
            self.drag_motion_intensity *= 0.88

        for index, label in enumerate(self.project_name_letters):
            delayed = max(0.0, self.drag_motion_intensity - (index * 1.15))
            offset = int(delayed * self.drag_motion_direction)
            if offset >= 0:
                label.setContentsMargins(offset, 4, 0, 4)
            else:
                label.setContentsMargins(0, 4, abs(offset), 4)
    
    def create_title_bar(self, layout: QVBoxLayout):
        """Create custom title bar (window controls only, no title)."""
        title_layout = QHBoxLayout()
        
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
        main_splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(main_splitter)
        
        # Left panel: File tree
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # Middle panel: Compile order
        middle_panel = self.create_middle_panel()
        main_splitter.addWidget(middle_panel)
        
        # Right panel: Output and controls
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions to favor the output pane and ensure middle column remains compact
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setStretchFactor(2, 5)
        main_splitter.setSizes([360, 180, 720])
    
    def create_project_controls(self, layout: QVBoxLayout):
        """Create project management controls with status bar integrated."""
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

        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self.rename_project)
        project_layout.addWidget(rename_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.open_settings_dialog)
        project_layout.addWidget(settings_btn)
        
        project_layout.addStretch()
        
        # Status and view controls
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #2e8b57; margin: 5px; font-weight: bold;")
        project_layout.addWidget(self.status_label)
        
        project_layout.addSpacing(20)
        
        # Zoom controls
        self.zoom_label = QLabel(f"Zoom: {int(self.zoom_level * 100)}%")
        self.zoom_label.setStyleSheet("margin: 5px;")
        project_layout.addWidget(self.zoom_label)
        
        self.scale_label = QLabel(f"Scale: {int(self.scale_factor * 100)}%")
        self.scale_label.setStyleSheet("margin: 5px;")
        project_layout.addWidget(self.scale_label)
        
        layout.addLayout(project_layout)
    
    def create_left_panel(self) -> QWidget:
        """Create the left panel with the checkbox file tree."""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        browser_label = QLabel("Project Tree")
        browser_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        left_layout.addWidget(browser_label)
        
        browser_controls = QHBoxLayout()
        
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.config.get_last_directory())
        self.path_edit.returnPressed.connect(self.navigate_to_path)
        browser_controls.addWidget(self.path_edit)

        up_btn = QPushButton("Up")
        up_btn.clicked.connect(self.navigate_to_parent_directory)
        browser_controls.addWidget(up_btn)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        browser_controls.addWidget(browse_btn)
        
        left_layout.addLayout(browser_controls)

        self.file_browser = FileBrowser(self.config)
        self.file_browser.selectionToggled.connect(self.on_browser_selection_toggled)
        self.file_browser.directoryChanged.connect(self.on_browser_directory_changed)
        left_layout.addWidget(self.file_browser, 1)
        left_widget.setMinimumWidth(260)

        return left_widget

    def create_middle_panel(self) -> QWidget:
        """Create the compile-order management column."""
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        middle_layout.setSpacing(10)

        files_label = QLabel("Compile Order")
        files_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        middle_layout.addWidget(files_label)

        filter_sort_row = QHBoxLayout()
        self.file_filter_edit = QLineEdit()
        self.file_filter_edit.setPlaceholderText("Filter selected files...")
        self.file_filter_edit.textChanged.connect(self.refresh_file_list)
        self.file_filter_edit.textChanged.connect(self.on_filter_text_changed)
        filter_sort_row.addWidget(self.file_filter_edit)

        self.file_sort_combo = QComboBox()
        self.file_sort_combo.addItems(["Manual", "Name ↑", "Name ↓", "Path ↑", "Path ↓"])
        self.file_sort_combo.currentTextChanged.connect(self.refresh_file_list)
        self.file_sort_combo.currentTextChanged.connect(self.on_sort_mode_changed)
        filter_sort_row.addWidget(self.file_sort_combo)
        middle_layout.addLayout(filter_sort_row)

        saved_filter = self.config.get_file_filter_text()
        if saved_filter:
            self.file_filter_edit.setText(saved_filter)

        saved_sort = self.config.get_file_sort_mode()
        saved_index = self.file_sort_combo.findText(saved_sort)
        if saved_index >= 0:
            self.file_sort_combo.setCurrentIndex(saved_index)
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.file_list.model().rowsMoved.connect(self.on_file_list_reordered)
        middle_layout.addWidget(self.file_list, 1)
        self.update_reorder_capability()
        middle_widget.setMinimumWidth(240)
        
        file_controls = QHBoxLayout()

        move_up_btn = QPushButton("Up")
        move_up_btn.clicked.connect(lambda: self.move_selected_files(-1))
        file_controls.addWidget(move_up_btn)

        move_down_btn = QPushButton("Down")
        move_down_btn.clicked.connect(lambda: self.move_selected_files(1))
        file_controls.addWidget(move_down_btn)
        
        remove_file_btn = QPushButton("Remove")
        remove_file_btn.clicked.connect(self.remove_selected_file)
        file_controls.addWidget(remove_file_btn)
        
        middle_layout.addLayout(file_controls)
        
        return middle_widget
    
    def create_right_panel(self) -> QWidget:
        """Create the right panel with output and controls."""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Compilation controls
        compile_layout = QHBoxLayout()
        
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
        right_widget.setMinimumWidth(520)
        right_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return right_widget
    
    def create_status_bar(self, layout: QVBoxLayout):
        """Create status bar (empty, status moved to top bar)."""
        pass  # Status bar components moved to top with project controls
    
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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_new.activated.connect(self.new_project)

        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.save_project)

        self.shortcut_load = QShortcut(QKeySequence("Ctrl+O"), self)
        self.shortcut_load.activated.connect(self.load_project)

        self.shortcut_compile = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.shortcut_compile.activated.connect(self.compile_files)

        self.shortcut_focus_filter = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_focus_filter.activated.connect(self.focus_file_filter)

        self.shortcut_remove = QShortcut(QKeySequence("Delete"), self)
        self.shortcut_remove.activated.connect(self.remove_selected_file)

    def focus_file_filter(self):
        """Focus the compile-order filter box."""
        if hasattr(self, "file_filter_edit"):
            self.file_filter_edit.setFocus()
            self.file_filter_edit.selectAll()
    
    def setup_gradient_outline(self):
        """Setup gradient outline that reacts to window position."""
        # This will be updated in paintEvent
        pass
    
    def restore_window_geometry(self):
        """Restore window geometry from settings."""
        geometry = self.config.get_window_geometry()
        try:
            if not os.environ.get('PYTEST_CURRENT_TEST'):
                self.setGeometry(geometry['x'], geometry['y'], geometry['width'], geometry['height'])
        except Exception:
            # Ignore geometry restoration failures in headless/test environments
            pass
    
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
            self.right_drag_press_position = event.globalPosition().toPoint()
            self.right_drag_moved = False
            self.suppress_context_menu_release = False
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
            new_position = event.globalPosition().toPoint()
            delta = new_position - self.drag_start_position
            self.move(self.pos() + delta)
            self.drag_start_position = new_position

            if (new_position - self.right_drag_press_position).manhattanLength() >= 6:
                self.right_drag_moved = True
                self.suppress_context_menu_release = True

            if delta.manhattanLength() > 0:
                self.drag_motion_intensity = min(18.0, max(self.drag_motion_intensity, delta.manhattanLength() * 0.45))
                self.drag_motion_direction = 1 if delta.x() >= 0 else -1
        
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
            if self.is_dragging and not self.is_resizing and not self.suppress_context_menu_release:
                release_delta = (event.globalPosition().toPoint() - self.right_drag_press_position).manhattanLength()
                if release_delta < 6 and not self.right_drag_moved:
                    self.show_context_menu(event.pos())
            
            self.is_dragging = False
            self.is_resizing = False
            self.right_drag_moved = False
            self.suppress_context_menu_release = False
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
            if hasattr(self, 'zoom_label'):
                self.zoom_label.setText(f"Zoom: {int(self.zoom_level * 100)}%")
            
        elif modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier) and event.buttons() == Qt.MouseButton.MiddleButton:
            # Scale window and contents
            delta = event.angleDelta().y() / 1200.0
            self.scale_factor = max(0.5, min(2.0, self.scale_factor + delta))
            self.config.set_scale_factor(self.scale_factor)
            self.apply_zoom_and_scale()
            if hasattr(self, 'scale_label'):
                self.scale_label.setText(f"Scale: {int(self.scale_factor * 100)}%")
        
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
        if hasattr(self, 'zoom_label'):
            self.zoom_label.setText(f"Zoom: {int(self.zoom_level * 100)}%")
    
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
            self.set_project_name_display(self.current_project_config.get_name())
            self.load_project_files()
    
    def save_project(self):
        """Save current project."""
        if self.current_project_config:
            self.current_project_config.set_files(list(self.project_files))
            self.current_project_config.set_browser_location(self.file_browser.current_directory)
            self.current_project_config.set_output_settings({
                'include_file_names': self.include_file_names_enabled,
                'include_file_tree': self.include_file_tree_enabled
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
                self.set_project_name_display(self.current_project_config.get_name())
                self.load_project_files()
                
                # Update browser location
                browser_location = self.current_project_config.get_browser_location()
                self.file_browser.navigate_to(browser_location)
                self.path_edit.setText(browser_location)
                
                # Update output settings
                output_settings = self.current_project_config.get_output_settings()
                self.include_file_names_enabled = bool(output_settings.get('include_file_names', True))
                self.include_file_tree_enabled = bool(output_settings.get('include_file_tree', True))
                self.config.set_include_file_names_enabled(self.include_file_names_enabled)
                self.config.set_include_file_tree_enabled(self.include_file_tree_enabled)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {e}")
    
    def load_project_files(self):
        """Load files from current project into the list."""
        if not self.current_project_config:
            return
        
        self.project_files = list(self.current_project_config.get_files())
        self.refresh_file_list()
        if hasattr(self, "file_browser"):
            self.file_browser.set_selected_files(self.project_files)
    
    def on_project_changed(self, project_name: str):
        """Handle project selection change."""
        # This would be implemented when project dropdown is fully functional
        pass

    def on_auto_populate_toggled(self, checked: bool):
        """Enable or disable directory auto-population."""
        self.auto_populate_enabled = checked
        self.config.set_auto_populate_enabled(checked)
        status = "enabled" if checked else "disabled"
        self.status_label.setText(f"Auto-populate {status}")
        QTimer.singleShot(1800, lambda: self.status_label.setText("Ready"))

    def on_exclude_empty_toggled(self, checked: bool):
        """Persist exclude-empty-files toggle setting."""
        self.exclude_empty_enabled = checked
        self.config.set_exclude_empty_enabled(checked)

    def open_settings_dialog(self):
        """Open settings dialog for compile and browser behavior toggles."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog_layout = QVBoxLayout(dialog)

        auto_populate_cb = QCheckBox("Auto-populate files when selecting a directory")
        auto_populate_cb.setChecked(self.auto_populate_enabled)
        dialog_layout.addWidget(auto_populate_cb)

        include_subdirs_cb = QCheckBox("Include sub-directories when auto-populating")
        include_subdirs_cb.setChecked(self.include_subdirectories_enabled)
        dialog_layout.addWidget(include_subdirs_cb)

        exclude_empty_cb = QCheckBox("Exclude empty files")
        exclude_empty_cb.setChecked(self.exclude_empty_enabled)
        dialog_layout.addWidget(exclude_empty_cb)

        include_names_cb = QCheckBox("Include file names in output")
        include_names_cb.setChecked(self.include_file_names_enabled)
        dialog_layout.addWidget(include_names_cb)

        include_tree_cb = QCheckBox("Include file tree in output")
        include_tree_cb.setChecked(self.include_file_tree_enabled)
        dialog_layout.addWidget(include_tree_cb)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        dialog_layout.addWidget(button_box)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.on_auto_populate_toggled(auto_populate_cb.isChecked())
            self.on_exclude_empty_toggled(exclude_empty_cb.isChecked())

            self.include_subdirectories_enabled = include_subdirs_cb.isChecked()
            self.config.set_include_subdirectories_enabled(self.include_subdirectories_enabled)

            self.include_file_names_enabled = include_names_cb.isChecked()
            self.config.set_include_file_names_enabled(self.include_file_names_enabled)

            self.include_file_tree_enabled = include_tree_cb.isChecked()
            self.config.set_include_file_tree_enabled(self.include_file_tree_enabled)

            self.status_label.setText("Settings updated")
            QTimer.singleShot(1800, lambda: self.status_label.setText("Ready"))

    def on_filter_text_changed(self, text: str):
        """Persist file list filter text."""
        self.config.set_file_filter_text(text)

    def on_sort_mode_changed(self, mode: str):
        """Persist file list sort mode."""
        self.config.set_file_sort_mode(mode)
    
    def on_browser_directory_changed(self, directory: str):
        """Keep browser path state in sync when the tree root changes."""
        self.path_edit.setText(directory)
        if self.current_project_config:
            self.current_project_config.set_browser_location(directory)
        self.file_browser.set_selected_files(self.project_files)

    def on_browser_selection_toggled(self, path: str, is_directory: bool, checked: bool):
        """Update ordered project files from checkbox tree interactions."""
        if is_directory:
            selected_paths = FileProcessor.collect_text_files(
                path,
                recursive=self.include_subdirectories_enabled,
                include_hidden=False,
            )
        else:
            selected_paths = [path]

        if checked:
            self.add_files_to_project(selected_paths)
        else:
            self.remove_files_from_project(selected_paths)

    def refresh_file_list(self):
        """Refresh compile-order list with active filter and sorting."""
        if not hasattr(self, "file_list"):
            return

        selected_paths = {item.data(Qt.ItemDataRole.UserRole) for item in self.file_list.selectedItems()}

        query = self.file_filter_edit.text().strip().lower() if hasattr(self, "file_filter_edit") else ""
        mode = self.file_sort_combo.currentText() if hasattr(self, "file_sort_combo") else "Name ↑"

        files = list(self.project_files)
        if query:
            files = [path for path in files if query in os.path.basename(path).lower() or query in path.lower()]

        if mode == "Name ↑":
            files.sort(key=lambda path: os.path.basename(path).lower())
        elif mode == "Name ↓":
            files.sort(key=lambda path: os.path.basename(path).lower(), reverse=True)
        elif mode == "Path ↑":
            files.sort(key=lambda path: path.lower())
        elif mode == "Path ↓":
            files.sort(key=lambda path: path.lower(), reverse=True)

        self.file_list.clear()
        for file_path in files:
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setToolTip(file_path)
            if FileProcessor.is_text_file(file_path):
                item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
            else:
                item.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
            self.file_list.addItem(item)
            if file_path in selected_paths:
                item.setSelected(True)

        self.update_reorder_capability()

    def update_reorder_capability(self):
        """Enable drag reordering only for manual, unfiltered mode."""
        if not hasattr(self, "file_list"):
            return

        query = self.file_filter_edit.text().strip() if hasattr(self, "file_filter_edit") else ""
        mode = self.file_sort_combo.currentText() if hasattr(self, "file_sort_combo") else "Manual"
        manual_mode = mode == "Manual"
        reorder_enabled = manual_mode and not query

        drag_mode = (QListWidget.DragDropMode.InternalMove if reorder_enabled
                     else QListWidget.DragDropMode.NoDragDrop)
        self.file_list.setDragDropMode(drag_mode)

        if reorder_enabled:
            self.file_list.setToolTip("Drag to reorder compile sequence")
        else:
            self.file_list.setToolTip("Clear filter and use Manual sort to reorder files")

    def on_file_list_reordered(self, *args):
        """Persist user-defined file order after drag-drop move."""
        if not hasattr(self, "file_sort_combo") or not hasattr(self, "file_filter_edit"):
            return

        if self.file_sort_combo.currentText() != "Manual":
            return

        if self.file_filter_edit.text().strip():
            return

        reordered = []
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            reordered.append(item.data(Qt.ItemDataRole.UserRole))

        self.project_files = reordered
        self.persist_project_files()

    def rename_project(self):
        """Rename the active project from the top bar action."""
        if not self.current_project_config:
            QMessageBox.information(self, "Rename Project", "Load or create a project first.")
            return

        current_name = self.current_project_config.get_name()
        new_name, ok = QInputDialog.getText(self, "Rename Project", "Project name:", text=current_name)
        if not ok:
            return

        normalized = new_name.strip()
        if not normalized:
            QMessageBox.warning(self, "Rename Project", "Project name cannot be empty.")
            return

        self.current_project_config.set_name(normalized)
        self.set_project_name_display(normalized)
        self.save_project()
        self.status_label.setText("Project renamed")
        QTimer.singleShot(1800, lambda: self.status_label.setText("Ready"))
    
    # File management methods
    def add_file_to_project(self, file_path: str):
        """Add a file to the current project."""
        self.add_files_to_project([file_path])

    def add_files_to_project(self, file_paths: Iterable[str]):
        """Append newly selected files while preserving current user order."""
        changed = False
        for file_path in file_paths:
            if not os.path.isfile(file_path):
                continue
            if not FileProcessor.is_text_file(file_path):
                continue
            if file_path in self.project_files:
                continue
            self.project_files.append(file_path)
            changed = True

        if not changed:
            self.file_browser.set_selected_files(self.project_files)
            return

        self.persist_project_files()
        self.refresh_file_list()
        self.file_browser.set_selected_files(self.project_files)

    def remove_files_from_project(self, file_paths: Iterable[str]):
        """Remove one or more files from the ordered compile list."""
        removal_set = set(file_paths)
        updated = [path for path in self.project_files if path not in removal_set]
        if len(updated) == len(self.project_files):
            self.file_browser.set_selected_files(self.project_files)
            return

        self.project_files = updated
        self.persist_project_files()
        self.refresh_file_list()
        self.file_browser.set_selected_files(self.project_files)

    def persist_project_files(self):
        """Persist the ordered file list into the active project config."""
        if self.current_project_config:
            self.current_project_config.set_files(list(self.project_files))
    
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
        selected_paths = [item.data(Qt.ItemDataRole.UserRole) for item in self.file_list.selectedItems()]
        if not selected_paths and self.file_list.currentItem():
            selected_paths = [self.file_list.currentItem().data(Qt.ItemDataRole.UserRole)]
        if selected_paths:
            self.remove_files_from_project(selected_paths)

    def move_selected_files(self, direction: int):
        """Move selected files up or down in manual compile order."""
        if direction not in (-1, 1):
            return
        if self.file_sort_combo.currentText() != "Manual" or self.file_filter_edit.text().strip():
            self.status_label.setText("Clear filter and use Manual sort to reorder")
            QTimer.singleShot(1800, lambda: self.status_label.setText("Ready"))
            return

        selected_paths = [item.data(Qt.ItemDataRole.UserRole) for item in self.file_list.selectedItems()]
        if not selected_paths:
            return

        selected_set = set(selected_paths)
        indices = [index for index, path in enumerate(self.project_files) if path in selected_set]
        if direction < 0:
            for index in indices:
                if index == 0 or self.project_files[index - 1] in selected_set:
                    continue
                self.project_files[index - 1], self.project_files[index] = self.project_files[index], self.project_files[index - 1]
        else:
            for index in reversed(indices):
                if index >= len(self.project_files) - 1 or self.project_files[index + 1] in selected_set:
                    continue
                self.project_files[index + 1], self.project_files[index] = self.project_files[index], self.project_files[index + 1]

        self.persist_project_files()
        self.refresh_file_list()
        visible_paths = {self.file_list.item(i).data(Qt.ItemDataRole.UserRole): self.file_list.item(i) for i in range(self.file_list.count())}
        for path in selected_paths:
            item = visible_paths.get(path)
            if item:
                item.setSelected(True)
    
    def clear_file_list(self):
        """Clear all files from the list."""
        self.project_files = []
        self.file_list.clear()
        self.persist_project_files()
        self.file_browser.set_selected_files(self.project_files)
    
    # Browser methods
    def navigate_to_path(self):
        """Navigate to the path in the path edit."""
        path = self.path_edit.text()
        if os.path.isdir(path):
            self.file_browser.navigate_to(path)

    def navigate_to_parent_directory(self):
        """Move the tree root to the parent directory of the current root."""
        current_directory = self.file_browser.current_directory
        parent_directory = os.path.dirname(current_directory.rstrip(os.sep)) or current_directory
        if parent_directory and parent_directory != current_directory:
            self.file_browser.navigate_to(parent_directory)
    
    def browse_directory(self):
        """Show directory browser dialog."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", 
            self.path_edit.text()
        )
        
        if directory:
            self.path_edit.setText(directory)
            self.file_browser.navigate_to(directory)
    
    # Compilation methods
    def compile_files(self):
        """Compile the selected files."""
        files = list(self.project_files)
        
        if not files:
            QMessageBox.warning(self, "Warning", "No files selected for compilation.")
            return
        
        # Prepare project config for compilation
        project_config = {
            'name': self.current_project_config.get_name() if self.current_project_config else "Untitled Project",
            'description': self.current_project_config.get_description() if self.current_project_config else "",
            'output_settings': {
                'include_file_names': self.include_file_names_enabled,
                'include_file_tree': self.include_file_tree_enabled
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
import os
import json
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QGridLayout,
    QFileDialog, QLabel, QHBoxLayout, QMessageBox, QScrollArea, QComboBox,
    QCheckBox, QSpinBox, QColorDialog, QMenu, QDialog, QFormLayout, QLineEdit
)
from PyQt6.QtCore import Qt, QPoint, QMimeData
from PyQt6.QtGui import QAction, QColor, QDrag, QIcon

SETTINGS_FILE = "launcher_settings.json"

class DraggableButton(QPushButton):
    def __init__(self, text, path, parent):
        super().__init__(text, parent)
        self.script_path = path

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            mime_data = QMimeData()
            mime_data.setText(self.script_path)
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec()

from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout

class SettingsDialog(QDialog):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.setWindowTitle("Launcher Settings")
        self.settings = settings

        self.tabs = QTabWidget(self)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)

        self.general_tab = QWidget()
        self.color_tab = QWidget()
        self.advanced_tab = QWidget()
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.color_tab, "Colors")
        self.tabs.addTab(self.advanced_tab, "Advanced")

        from PyQt6.QtWidgets import QSlider
        layout = QFormLayout(self.general_tab)

        self.cols_input = QSpinBox()
        self.cols_input.setMinimum(1)
        self.cols_input.setMaximum(10)
        self.cols_input.setValue(self.settings.get("cols", 4))

        self.button_height_input = QSlider(Qt.Orientation.Horizontal)
        self.button_height_input.setMinimum(20)
        self.button_height_input.setMaximum(200)
        self.button_height_input.setValue(self.settings.get("button_height", 40))

        layout.addRow("Grid Columns:", self.cols_input)
        layout.addRow("Button Height (px):", self.button_height_input)
        self.arrangement_order = QComboBox()
        self.arrangement_order.addItems(["Alphabetical", "Custom", "Last Modified"])
        current_order = "Alphabetical" if self.settings.get("alpha_order", True) else "Custom"
        self.arrangement_order.setCurrentText(current_order)
        layout.addRow("Arrangement Order:", self.arrangement_order)

        self.button_height_input = QSlider(Qt.Orientation.Horizontal)
        self.button_height_input.setMinimum(20)
        self.button_height_input.setMaximum(200)
        self.button_height_input.setValue(self.settings.get("button_height", 40))

        self.cols_input = QSpinBox()
        self.cols_input.setMinimum(1)
        self.cols_input.setMaximum(10)
        self.cols_input.setValue(self.settings.get("cols", 4))

        self.alpha_order_cb = QCheckBox("Alphabetical Order")
        self.alpha_order_cb.setChecked(self.settings.get("alpha_order", True))

        self.highlight_new_cb = QCheckBox("Highlight New Scripts")
        self.highlight_new_cb.setChecked(self.settings.get("highlight_new", True))

        self.default_color_picker = QPushButton()
        self.default_color_picker.setStyleSheet(f"background-color: {self.settings.get('default_color', '#f0f0f0')}")
        self.default_color_picker.clicked.connect(lambda: self.pick_color("default_color", self.default_color_picker))

        self.outline_color_picker = QPushButton()
        self.outline_color_picker.setStyleSheet(f"background-color: {self.settings.get('new_outline_color', '#ff0000')}")
        self.outline_color_picker.clicked.connect(lambda: self.pick_color("new_outline_color", self.outline_color_picker))

        self.font_color_picker = QPushButton("Select Font Color")
        self.font_color_picker.setStyleSheet(f"background-color: {self.settings.get('font_color', '#000000')}")
        self.font_color_picker.clicked.connect(lambda: self.pick_color("font_color", self.font_color_picker))

        self.folder_color_picker = QPushButton()
        self.folder_color_picker.setStyleSheet(f"background-color: {self.settings.get('folder_color', '#dddddd')}")
        self.folder_color_picker.clicked.connect(lambda: self.pick_color("folder_color", self.folder_color_picker))

        self.folder_outline_picker = QPushButton()
        self.folder_outline_picker.setStyleSheet(f"background-color: {self.settings.get('folder_outline_color', '#aaaaaa')}")
        self.folder_outline_picker.clicked.connect(lambda: self.pick_color("folder_outline_color", self.folder_outline_picker))

        

        color_layout = QFormLayout(self.color_tab)
        color_layout.addRow("Default Button Color:", self.default_color_picker)
        color_layout.addRow("New Script Outline Color:", self.outline_color_picker)
        color_layout.addRow("Font Color:", self.font_color_picker)
        color_layout.addRow("Folder Button Color:", self.folder_color_picker)
        color_layout.addRow("Folder Outline Color:", self.folder_outline_picker)

        adv_layout = QFormLayout(self.advanced_tab)
        self.blacklist_editor = QLineEdit(", ".join(self.settings.get("blacklist", [])))
        adv_layout.addRow("Blacklisted Items:", self.blacklist_editor)

        from PyQt6.QtWidgets import QHBoxLayout

        self.folder_path_display = QLabel(self.settings.get("last_folder", ""))
        folder_row = QHBoxLayout()
        folder_btn = QPushButton("Browse")
        folder_btn.clicked.connect(self.select_script_folder)
        folder_row.addWidget(self.folder_path_display)
        folder_row.addWidget(folder_btn)
        adv_layout.addRow("Script Root Folder:", folder_row)

        reset_btn = QPushButton("Reset All Settings")
        reset_btn.clicked.connect(self.reset_all_settings)
        export_btn = QPushButton("Export Settings to JSON")
        export_btn.clicked.connect(self.export_settings)

        import_btn = QPushButton("Import Settings from JSON")
        import_btn.clicked.connect(self.import_settings)

        adv_layout.addRow(export_btn)
        adv_layout.addRow(import_btn)
        adv_layout.addRow(reset_btn)

        self.accepted.connect(self.apply_changes)

    def pick_color(self, key, button):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings[key] = color.name()
            button.setStyleSheet(f"background-color: {color.name()}")

    def select_script_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Script Directory")
        if folder:
            self.settings["last_folder"] = folder
            self.folder_path_display.setText(folder)

    def export_settings(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Settings", "settings.json", "JSON Files (*.json)")
        if path:
            with open(path, "w") as f:
                json.dump(self.settings, f, indent=2)

    def import_settings(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Settings", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "r") as f:
                    imported = json.load(f)
                    self.settings.clear()
                    self.settings.update(imported)
                    self.close()
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", f"Error loading settings: {e}")

    def reset_all_settings(self):
        default = self.parent().settings.__class__()
        self.settings.clear()
        self.settings.update(default)
        self.close()

    def apply_changes(self):
        selected_order = self.arrangement_order.currentText()
        self.settings["alpha_order"] = (selected_order == "Alphabetical")
        self.settings["order_mode"] = selected_order
        self.settings["button_height"] = self.button_height_input.value()
        self.settings["cols"] = self.cols_input.value()
        # removed duplicate alpha_order setting line
        self.settings["highlight_new"] = self.highlight_new_cb.isChecked()
        self.settings["blacklist"] = [s.strip() for s in self.blacklist_editor.text().split(',') if s.strip()]
        self.settings["last_folder"] = self.folder_path_input.text()

from PyQt6.QtGui import QMouseEvent

class ScriptLauncher(QWidget):
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.RightButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    def eventFilter(self, obj, event):
        if event.type() == event.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            self.close()
            return True
        return super().eventFilter(obj, event)


    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("Python Script Launcher")

        self.script_dir = None
        self.scripts = []
        self.folder_contents = []
        self.settings = {
            "blacklist": [],
            "folder_color": "#dddddd",
            "folder_outline_color": "#aaaaaa",
            "highlight_new": True,
            "button_icons": {},
            "cols": 4,
            "alpha_order": True,
            "excluded": [],
            "pinned": [],
            "layout_order": [],
            "button_colors": {},
            "default_color": "#f0f0f0",
            "new_outline_color": "#ff0000",
            "button_height": 40,
            "font_color": "#000000"
        }
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.init_controls()
        self.init_script_grid()
        self.load_settings()

    def init_controls(self):
        control_layout = QHBoxLayout()

        self.fav_layout = QGridLayout()
        self.fav_layout.setSpacing(4)
        self.fav_layout.setContentsMargins(4, 4, 4, 4)
        self.favorite_buttons = {}

        self.back_btn = QPushButton("<")
        self.back_btn.setFixedSize(30, 30)
        self.back_btn.clicked.connect(self.go_back)
        control_layout.addWidget(self.back_btn)

        self.fav_layout.setSpacing(4)
        self.fav_layout.setContentsMargins(4, 4, 4, 4)
        self.favorite_buttons = {}
        control_layout.addLayout(self.fav_layout)

        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(30, 30)
        settings_btn.clicked.connect(self.show_settings_dialog)
        control_layout.addWidget(settings_btn)

        self.main_layout.addLayout(control_layout)

        
    def toggle_always_on_top(self):
        current = self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, not current)
        self.show()

    def show_settings_dialog(self):
        dlg = SettingsDialog(self, self.settings)
        dlg.exec()
        self.save_settings()
        self.scan_scripts()
        self.refresh_scripts()
        self.settings["known_scripts"] = self.scripts
        self.save_settings()

    
    def init_script_grid(self):
        self.script_grid = QGridLayout()
        self.scroll_area = QScrollArea()
        inner_widget = QWidget()
        inner_widget.setLayout(self.script_grid)
        self.scroll_area.setWidget(inner_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAcceptDrops(True)
        self.scroll_area.dragEnterEvent = self.dragEnterEvent
        self.scroll_area.dropEvent = self.dropEvent
        self.main_layout.addWidget(self.scroll_area)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        script_path = event.mimeData().text()
        if script_path in self.scripts:
            self.settings["layout_order"].insert(0, script_path)
            self.refresh_scripts()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Script Directory")
        if folder:
            self.script_dir = folder
            self.scan_scripts()
            self.refresh_scripts()

    def enter_folder(self, path):
        self.script_dir = path
        self.scan_scripts()
        self.refresh_scripts()

    def scan_scripts(self):
        blacklist = set(self.settings.get("blacklist", []))
        self.old_scripts = set(self.settings.get("known_scripts", []))
        self.previous_scripts = set(self.scripts)
        self.scripts = []
        self.folder_contents = []
        if not os.path.isdir(self.script_dir):
            return

        for entry in os.scandir(self.script_dir):
            if entry.path in blacklist:
                continue
            if entry.is_dir():
                self.folder_contents.append((entry.name, 'folder', entry.path))
            elif entry.name.endswith(".py"):
                self.scripts.append(entry.path)
                self.folder_contents.append((entry.name, 'script', entry.path))

    def add_back_button(self):
        back_btn = QPushButton("<")
        back_btn.clicked.connect(self.go_back)
        self.script_grid.addWidget(back_btn, 0, 0)

    def go_back(self):
        parent = os.path.abspath(os.path.dirname(self.script_dir))
        root = os.path.abspath(self.settings.get("last_folder", ""))
        if os.path.isdir(parent) and os.path.commonpath([parent, root]) == root and parent != self.script_dir:
            self.script_dir = parent
            self.scan_scripts()
            self.refresh_scripts()

    def handle_grid_drop(self, event, target_path):
        if not self.settings.get("alpha_order", True):
            if event.mimeData().hasText():
                source_path = event.mimeData().text()
                if source_path != target_path:
                    layout = self.settings.get("layout_order", [])
                    if source_path in layout:
                        layout.remove(source_path)
                    if target_path in layout:
                        index = layout.index(target_path)
                        layout.insert(index, source_path)
                    else:
                        layout.append(source_path)
                    self.settings["layout_order"] = layout
                    self.save_settings()
                    self.refresh_scripts()

    def update_back_button_visibility(self):
        root = os.path.abspath(self.settings.get("last_folder", ""))
        self.back_btn.setVisible(os.path.abspath(self.script_dir) != root)

    def refresh_scripts(self):
        order_mode = self.settings.get("order_mode", "Alphabetical")
        for i in reversed(range(self.script_grid.count())):
            self.script_grid.itemAt(i).widget().setParent(None)

        items = self.folder_contents[:]
        if order_mode == "Alphabetical":
            items.sort(key=lambda x: x[0])
        elif order_mode == "Last Modified":
            items.sort(key=lambda x: os.path.getmtime(x[2]), reverse=True)
        elif order_mode == "Custom":
            layout_order = self.settings.get("layout_order", [])
            items.sort(key=lambda x: layout_order.index(x[2]) if x[2] in layout_order else len(layout_order))

        self.update_back_button_visibility()
        row, col = 1, 0
        for name, typ, path in items:
            if path in self.settings["pinned"]:
                continue
            if typ == 'folder':
                formatted_name = name.replace('_', ' ').replace('-', ' ').split('.')[0].title()
                btn = QPushButton(f"📁 {formatted_name}")
                icon_path = self.settings.get("button_icons", {}).get(path)
                if icon_path and os.path.exists(icon_path):
                    btn.setIcon(QIcon(icon_path))
                    btn.setText(formatted_name)  # remove folder emoji
                folder_color = self.settings.get("button_colors", {}).get(path, self.settings.get("folder_color", "#dddddd"))
                folder_outline = self.settings.get("folder_outline_color", "#aaaaaa")
                btn.setStyleSheet(f"background-color: {folder_color}; border: 2px solid {folder_outline}; height: {self.settings['button_height']}px")
                btn.clicked.connect(lambda _, p=path: self.middle_click_run_or_open(p))
                btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda point, p=path, b=btn: self.show_context_menu(point, p, b))
                btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda point, p=path, b=btn: self.show_context_menu(point, p, b))
                folder_color = self.settings.get("folder_color", "#dddddd")
                folder_outline = self.settings.get("folder_outline_color", "#aaaaaa")
                btn.setStyleSheet(f"background-color: {folder_color}; border: 2px solid {folder_outline}; height: {self.settings['button_height']}px")
            else:
                formatted_name = name.replace('_', ' ').replace('-', ' ').split('.')[0].title()
                btn = DraggableButton(formatted_name, path, self)
                icon_path = self.settings.get("button_icons", {}).get(path)
                if icon_path and os.path.exists(icon_path):
                    btn.setIcon(QIcon(icon_path))
                color = self.settings["button_colors"].get(path, self.settings["default_color"])
                highlight = ""
                if path not in self.previous_scripts and self.settings.get("highlight_new", True):
                    outline_color = self.settings.get("new_outline_color", "#ff0000")
                    highlight = f"; border: 2px solid {outline_color}"
                font_color = self.settings.get("button_font_colors", {}).get(path, self.settings.get("font_color", "#000000"))
                btn.setStyleSheet(f"background-color: {color}; color: {font_color}; height: {self.settings['button_height']}px{highlight}")
                btn.clicked.connect(lambda _, p=path: self.middle_click_run_or_open(p))
                btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda point, p=path, b=btn: self.show_context_menu(point, p, b))

            btn.setToolTip(path)
            btn.setAcceptDrops(True)
            btn.dragEnterEvent = self.dragEnterEvent
            btn.dropEvent = lambda e, p=path: self.handle_grid_drop(e, p)
            self.script_grid.addWidget(btn, row, col)
            col += 1
            if col >= self.settings["cols"]:
                col = 0
                row += 1

    def refresh_favorites(self):
        for i in reversed(range(self.fav_layout.count())):
            self.fav_layout.itemAt(i).widget().setParent(None)

        self.fav_layout.setSpacing(4)
        self.fav_layout.setContentsMargins(4, 4, 4, 4)
        self.favorite_buttons = {}

        row, col = 0, 0
        for path in self.settings["pinned"]:
            btn = QPushButton("★ " + os.path.basename(path))
            icon_path = self.settings.get("button_icons", {}).get(path)
            if icon_path and os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
            color = self.settings["button_colors"].get(path, self.settings["default_color"])
            font_color = self.settings.get("font_color", "#000000")
            btn.setStyleSheet(f"background-color: {color}; color: {font_color}; height: {self.settings['button_height']}px")
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda point, p=path, b=btn: self.show_favorite_context_menu(point, p, b))
            btn.clicked.connect(lambda _, p=path: self.run_script(p))
            btn.setAcceptDrops(True)
            btn.dragEnterEvent = self.dragEnterEvent
            btn.dropEvent = lambda e, p=path: self.handle_favorite_drop(e, p)
            self.favorite_buttons[path] = btn
            self.fav_layout.addWidget(btn, row, col)
            col += 1
            if col >= self.settings["cols"]:
                col = 0
                row += 1

    def middle_click_run_or_open(self, path):
        if QApplication.mouseButtons() == Qt.MouseButton.MiddleButton:
            if os.path.isdir(path):
                subprocess.Popen(['explorer', path])
            else:
                self.run_script(path)
            self.close()
        else:
            if os.path.isdir(path):
                self.enter_folder(path)
            else:
                self.run_script(path)

    def run_script(self, path):
        try:
            if path.endswith(".py"):
                subprocess.Popen(["python", path])
            elif path.endswith(".sh"):
                subprocess.Popen(["bash", path])
            elif path.endswith(".ps1"):
                subprocess.Popen(["powershell", "-ExecutionPolicy", "Bypass", "-File", path])
            else:
                QMessageBox.warning(self, "Unsupported", f"File type not supported: {path}")
                return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not run script:\n{e}")

    def show_context_menu(self, point: QPoint, script_path: str, button: QPushButton):
        menu = QMenu(self)
        top_action = QAction("Toggle Always on Top", self)
        top_action.triggered.connect(self.toggle_always_on_top)
        color_action = QAction("Change Button Color", self)
        color_action.triggered.connect(lambda: self.change_button_color(script_path, button))
        pin_action = QAction("Pin to Favorites", self)
        pin_action.triggered.connect(lambda: self.pin_script(script_path))
        icon_action = QAction("Set Button Icon", self)
        icon_action.triggered.connect(lambda: self.set_button_icon(script_path, button))
        menu.addAction(color_action)
        menu.addAction(pin_action)
        hide_action = QAction("Hide This Item", self)
        hide_action.triggered.connect(lambda: self.hide_entry(script_path))
        explorer_action = QAction("Open in Explorer", self)
        explorer_action.triggered.connect(lambda: subprocess.Popen(['explorer', os.path.dirname(script_path) if os.path.isfile(script_path) else script_path]))
        menu.addAction(explorer_action)
        font_action = QAction("Set Font Color", self)
        font_action.triggered.connect(lambda: self.change_font_color(script_path, button))
        menu.addAction(font_action)
        menu.addAction(icon_action)
        menu.addAction(hide_action)
        menu.popup(button.mapToGlobal(point))

    def change_font_color(self, path, button):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings.setdefault("button_font_colors", {})[path] = color.name()
            self.save_settings()
            self.refresh_scripts()

    def change_button_color(self, path, button):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            self.settings["button_colors"][path] = hex_color
            button.setStyleSheet(f"background-color: {hex_color}")
            self.save_settings()

    def hide_entry(self, path):
        if path not in self.settings["blacklist"]:
            self.settings["blacklist"].append(path)
            self.save_settings()
            self.scan_scripts()
            self.refresh_scripts()

    def set_button_icon(self, path, button):
        icon_path, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Images (*.png *.xpm *.jpg *.ico)")
        if icon_path:
            button.setIcon(QIcon(icon_path))
            self.settings.setdefault("button_icons", {})[path] = icon_path
            self.save_settings()

    def pin_script(self, path):
        if path not in self.settings["pinned"]:
            self.settings["pinned"].append(path)
            self.save_settings()
            self.refresh_favorites()
            self.refresh_scripts()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                self.settings.update(json.load(f))

        last = self.settings.get("last_folder")
        if last and os.path.isdir(last):
            self.script_dir = last
            self.scan_scripts()
            self.refresh_scripts()

        self.refresh_favorites()

        last = self.settings.get("last_folder")
        if last and os.path.isdir(last):
            self.script_dir = last
            self.scan_scripts()
            self.refresh_scripts()

    def show_favorite_context_menu(self, point: QPoint, script_path: str, button: QPushButton):
        menu = QMenu(self)
        color_action = QAction("Change Button Color", self)
        color_action.triggered.connect(lambda: self.change_button_color(script_path, button))
        unpin_action = QAction("Remove from Favorites", self)
        unpin_action.triggered.connect(lambda: self.unpin_script(script_path))
        icon_action = QAction("Set Button Icon", self)
        icon_action.triggered.connect(lambda: self.set_button_icon(script_path, button))
        menu.addAction(color_action)
        menu.addAction(icon_action)
        menu.addAction(top_action)
        menu.addAction(unpin_action)
        menu.exec(button.mapToGlobal(point))

    def handle_favorite_drop(self, event, target_path):
        if event.mimeData().hasText():
            source_path = event.mimeData().text()
            if source_path in self.settings["pinned"] and target_path in self.settings["pinned"]:
                s_idx = self.settings["pinned"].index(source_path)
                t_idx = self.settings["pinned"].index(target_path)
                self.settings["pinned"].insert(t_idx, self.settings["pinned"].pop(s_idx))
                self.save_settings()
                self.refresh_favorites()

    def unpin_script(self, path):
        if path in self.settings["pinned"]:
            self.settings["pinned"].remove(path)
            self.save_settings()
            self.refresh_favorites()
            self.refresh_scripts()

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=2)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = ScriptLauncher()
    win.resize(800, 600)
    win.show()
    app.installEventFilter(win)
    sys.exit(app.exec())

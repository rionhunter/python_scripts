import os
import json
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QGridLayout,
    QFileDialog, QLabel, QHBoxLayout, QMessageBox, QScrollArea, QComboBox,
    QCheckBox, QSpinBox, QColorDialog, QMenu, QDialog, QFormLayout, QLineEdit
)
from PyQt6.QtCore import Qt, QPoint, QMimeData
from PyQt6.QtGui import QAction, QColor, QDrag

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

class SettingsDialog(QDialog):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.setWindowTitle("Launcher Settings")
        self.settings = settings
        layout = QFormLayout(self)

        self.default_color_input = QLineEdit(self.settings.get("default_color", "#f0f0f0"))
        self.outline_color_input = QLineEdit(self.settings.get("new_outline_color", "#ff0000"))
        self.button_height_input = QSpinBox()
        self.button_height_input.setMinimum(20)
        self.button_height_input.setMaximum(200)
        self.button_height_input.setValue(self.settings.get("button_height", 40))

        layout.addRow("Default Button Color:", self.default_color_input)
        layout.addRow("New Script Outline Color:", self.outline_color_input)
        layout.addRow("Button Height:", self.button_height_input)

        self.accepted.connect(self.apply_changes)

    def apply_changes(self):
        self.settings["default_color"] = self.default_color_input.text()
        self.settings["new_outline_color"] = self.outline_color_input.text()
        self.settings["button_height"] = self.button_height_input.value()

class ScriptLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Script Launcher")

        self.script_dir = None
        self.scripts = []
        self.pinned = []
        self.layout_order = []
        self.button_colors = {}
        self.settings = {
            "button_icons": {},
            "rows": 4,
            "cols": 4,
            "fav_rows": 1,
            "alpha_order": True,
            "excluded": [],
            "pinned": [],
            "layout_order": [],
            "button_colors": {},
            "default_color": "#f0f0f0",
            "new_outline_color": "#ff0000",
            "button_height": 40
        }
        self.load_settings()

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.init_controls()
        self.init_favorites()
        self.init_script_grid()

    def init_controls(self):
        control_layout = QHBoxLayout()
        browse_btn = QPushButton("Select Folder")
        browse_btn.clicked.connect(self.select_folder)
        control_layout.addWidget(browse_btn)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.show_settings_dialog)
        control_layout.addWidget(settings_btn)

        self.rows_input = QSpinBox()
        self.rows_input.setValue(self.settings["rows"])
        self.rows_input.setMinimum(1)
        self.rows_input.setMaximum(10)
        self.rows_input.valueChanged.connect(self.refresh_scripts)
        control_layout.addWidget(QLabel("Grid Rows:"))
        control_layout.addWidget(self.rows_input)

        self.cols_input = QSpinBox()
        self.cols_input.setValue(self.settings["cols"])
        self.cols_input.setMinimum(1)
        self.cols_input.setMaximum(10)
        self.cols_input.valueChanged.connect(self.refresh_scripts)
        control_layout.addWidget(QLabel("Grid Columns:"))
        control_layout.addWidget(self.cols_input)

        self.alpha_order_cb = QCheckBox("Alphabetical Order")
        self.alpha_order_cb.setChecked(self.settings["alpha_order"])
        self.alpha_order_cb.stateChanged.connect(self.refresh_scripts)
        control_layout.addWidget(self.alpha_order_cb)

        self.main_layout.addLayout(control_layout)

    def show_settings_dialog(self):
        dlg = SettingsDialog(self, self.settings)
        dlg.exec()
        self.save_settings()
        self.refresh_scripts()

    def init_favorites(self):
        self.fav_layout = QGridLayout()
        self.main_layout.addLayout(self.fav_layout)
        self.refresh_favorites()

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

    def scan_scripts(self):
        self.previous_scripts = set(self.scripts)  # Capture existing list for change detection
        self.scripts = []
        self.scripts = []
        for root, dirs, files in os.walk(self.script_dir):
            if any(ex in root for ex in self.settings["excluded"]):
                continue
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    self.scripts.append(full_path)

    def refresh_scripts(self):
        self.settings["rows"] = self.rows_input.value()
        self.settings["cols"] = self.cols_input.value()
        self.settings["alpha_order"] = self.alpha_order_cb.isChecked()
        self.save_settings()

        for i in reversed(range(self.script_grid.count())):
            self.script_grid.itemAt(i).widget().setParent(None)

        script_paths = self.scripts[:]
        if self.settings["alpha_order"]:
            script_paths.sort()
        elif self.settings["layout_order"]:
            script_paths.sort(key=lambda x: self.settings["layout_order"].index(x)
                              if x in self.settings["layout_order"] else len(self.settings["layout_order"]))

        row, col = 0, 0
        for path in script_paths:
            if path in self.settings["pinned"]:
                continue
            btn = DraggableButton(os.path.basename(path), path, self)
            icon_path = self.settings.get("button_icons", {}).get(path)
            if icon_path and os.path.exists(icon_path):
                from PyQt6.QtGui import QIcon
                btn.setIcon(QIcon(icon_path))
            btn.setToolTip(path)
            btn.clicked.connect(lambda _, p=path: self.run_script(p))
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda point, p=path, b=btn: self.show_context_menu(point, p, b))
            color = self.settings["button_colors"].get(path, self.settings["default_color"])
            highlight = ""
            if path not in self.previous_scripts:
                outline_color = self.settings.get("new_outline_color", "#ff0000")
                highlight = f"; border: 2px solid {outline_color}"
            btn.setStyleSheet(f"background-color: {color}; height: {self.settings['button_height']}px" + highlight)
            self.script_grid.addWidget(btn, row, col)
            col += 1
            if col >= self.settings["cols"]:
                col = 0
                row += 1

    def refresh_favorites(self):
        for i in reversed(range(self.fav_layout.count())):
            self.fav_layout.itemAt(i).widget().setParent(None)

        row, col = 0, 0
        for path in self.settings["pinned"]:
            btn = QPushButton("★ " + os.path.basename(path))
            btn.setToolTip(path)
            btn.clicked.connect(lambda _, p=path: self.run_script(p))
            self.fav_layout.addWidget(btn, row, col)
            col += 1
            if col >= self.settings["cols"]:
                col = 0
                row += 1

    def run_script(self, path):
        try:
            subprocess.Popen(["python", path])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not run script:\n{e}")

    def show_context_menu(self, point: QPoint, script_path: str, button: QPushButton):
        from PyQt6.QtWidgets import QFileDialog
        from PyQt6.QtGui import QIcon
        menu = QMenu(self)

        color_action = QAction("Change Button Color", self)
        color_action.triggered.connect(lambda: self.change_button_color(script_path, button))

        pin_action = QAction("Pin to Favorites", self)
        pin_action.triggered.connect(lambda: self.pin_script(script_path))

        icon_action = QAction("Set Button Icon", self)
        icon_action.triggered.connect(lambda: self.set_button_icon(script_path, button))

        menu.addAction(color_action)
        menu.addAction(pin_action)
        menu.addAction(icon_action)

        menu.exec(button.mapToGlobal(point))
        menu = QMenu(self)
        color_action = QAction("Change Button Color", self)
        color_action.triggered.connect(lambda: self.change_button_color(script_path, button))
        pin_action = QAction("Pin to Favorites", self)
        pin_action.triggered.connect(lambda: self.pin_script(script_path))
        menu.addAction(color_action)
        menu.addAction(pin_action)
        menu.exec(button.mapToGlobal(point))

    def change_button_color(self, path, button):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            self.settings["button_colors"][path] = hex_color
            button.setStyleSheet(f"background-color: {hex_color}")
            self.save_settings()

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

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=2)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = ScriptLauncher()
    win.resize(800, 600)
    win.show()
    sys.exit(app.exec())

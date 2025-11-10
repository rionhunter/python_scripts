"""
Modern Macro Manager - Sleek glassmorphism UI for multi-device macro automation
Supports: Secondary keyboards, game controllers, MIDI devices, text commands, AI dictation
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QListWidget, 
                            QScrollArea, QFrame, QLineEdit, QComboBox, 
                            QSpinBox, QTextEdit, QFileDialog, QListWidgetItem,
                            QDialog, QDialogButtonBox, QGridLayout, QCheckBox,
                            QTabWidget, QStackedWidget, QSplitter)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt6.QtGui import (QPalette, QColor, QPainter, QBrush, QPen, 
                        QLinearGradient, QFont, QPixmap, QIcon)


class GlassWidget(QWidget):
    """Base widget with glassmorphism effect"""
    
    def __init__(self, parent=None, blur_radius=20, opacity=0.15):
        super().__init__(parent)
        self.blur_radius = blur_radius
        self.bg_opacity = opacity
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create glass effect
        rect = self.rect()
        
        # Dark background with transparency
        painter.setBrush(QBrush(QColor(0, 0, 0, int(255 * self.bg_opacity))))
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 12, 12)
        
        # Subtle gradient overlay
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 25))
        gradient.setColorAt(1, QColor(255, 255, 255, 5))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 12, 12)


class MacroAction:
    """Represents a single macro action"""
    
    ACTION_TYPES = [
        "Keyboard Press",
        "Text Paste", 
        "Mouse Click",
        "Mouse Move",
        "Wait",
        "Open File",
        "Open URL",
        "Open Application",
        "Switch Application",
        "Run Script"
    ]
    
    def __init__(self, action_type="Keyboard Press", params=None):
        self.action_type = action_type
        self.params = params or {}
        
    def to_dict(self):
        return {
            "action_type": self.action_type,
            "params": self.params
        }
    
    @staticmethod
    def from_dict(data):
        return MacroAction(data.get("action_type"), data.get("params", {}))
    
    def __str__(self):
        if self.action_type == "Keyboard Press":
            return f"Press: {self.params.get('key', 'Unknown')}"
        elif self.action_type == "Text Paste":
            text = self.params.get('text', '')
            preview = text[:30] + "..." if len(text) > 30 else text
            return f"Paste: {preview}"
        elif self.action_type == "Mouse Click":
            return f"Click: {self.params.get('button', 'Left')} at ({self.params.get('x', 0)}, {self.params.get('y', 0)})"
        elif self.action_type == "Wait":
            return f"Wait: {self.params.get('duration', 0)}ms"
        elif self.action_type == "Open File":
            return f"Open: {Path(self.params.get('path', '')).name}"
        elif self.action_type == "Open URL":
            return f"URL: {self.params.get('url', '')}"
        elif self.action_type == "Open Application":
            return f"Launch: {self.params.get('app_name', 'Unknown')}"
        elif self.action_type == "Switch Application":
            return f"Switch to: {self.params.get('app_name', 'Unknown')}"
        elif self.action_type == "Run Script":
            return f"Script: {Path(self.params.get('script_path', '')).name}"
        return self.action_type


class Macro:
    """Represents a complete macro with multiple actions"""
    
    def __init__(self, name="New Macro", actions=None, trigger=None, dynamic=False):
        self.name = name
        self.actions = actions or []
        self.trigger = trigger or {}
        self.dynamic = dynamic  # Can accept runtime variables
        self.enabled = True
        
    def to_dict(self):
        return {
            "name": self.name,
            "actions": [action.to_dict() for action in self.actions],
            "trigger": self.trigger,
            "dynamic": self.dynamic,
            "enabled": self.enabled
        }
    
    @staticmethod
    def from_dict(data):
        macro = Macro(
            data.get("name", "New Macro"),
            [MacroAction.from_dict(a) for a in data.get("actions", [])],
            data.get("trigger", {}),
            data.get("dynamic", False)
        )
        macro.enabled = data.get("enabled", True)
        return macro


class ActionEditorDialog(QDialog):
    """Dialog for editing individual macro actions"""
    
    def __init__(self, action=None, parent=None):
        super().__init__(parent)
        self.action = action or MacroAction()
        self.setWindowTitle("Edit Action")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Action type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Action Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(MacroAction.ACTION_TYPES)
        self.type_combo.setCurrentText(self.action.action_type)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Stacked widget for different parameter inputs
        self.param_stack = QStackedWidget()
        
        # Create parameter widgets for each action type
        self.param_widgets = {
            "Keyboard Press": self.create_keyboard_params(),
            "Text Paste": self.create_text_params(),
            "Mouse Click": self.create_mouse_click_params(),
            "Mouse Move": self.create_mouse_move_params(),
            "Wait": self.create_wait_params(),
            "Open File": self.create_file_params(),
            "Open URL": self.create_url_params(),
            "Open Application": self.create_app_params(),
            "Switch Application": self.create_switch_app_params(),
            "Run Script": self.create_script_params()
        }
        
        for widget in self.param_widgets.values():
            self.param_stack.addWidget(widget)
            
        layout.addWidget(self.param_stack)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Load current action
        self.on_type_changed(self.action.action_type)
        self.load_params()
        
    def create_keyboard_params(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Key or Hotkey:"))
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("e.g., 'a', 'ctrl+c', 'shift+alt+t'")
        layout.addWidget(self.key_input)
        
        self.key_hold_check = QCheckBox("Hold key down")
        layout.addWidget(self.key_hold_check)
        
        layout.addStretch()
        return widget
    
    def create_text_params(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Text to paste:"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter text to paste...")
        layout.addWidget(self.text_input)
        
        self.variable_check = QCheckBox("Contains variables (e.g., {var_name})")
        layout.addWidget(self.variable_check)
        
        return widget
    
    def create_mouse_click_params(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(QLabel("Button:"))
        self.mouse_button = QComboBox()
        self.mouse_button.addItems(["Left", "Right", "Middle"])
        button_layout.addWidget(self.mouse_button)
        layout.addLayout(button_layout)
        
        pos_layout = QGridLayout()
        pos_layout.addWidget(QLabel("X:"), 0, 0)
        self.mouse_x = QSpinBox()
        self.mouse_x.setRange(-10000, 10000)
        pos_layout.addWidget(self.mouse_x, 0, 1)
        
        pos_layout.addWidget(QLabel("Y:"), 0, 2)
        self.mouse_y = QSpinBox()
        self.mouse_y.setRange(-10000, 10000)
        pos_layout.addWidget(self.mouse_y, 0, 3)
        
        layout.addLayout(pos_layout)
        
        self.mouse_relative = QCheckBox("Relative to current position")
        layout.addWidget(self.mouse_relative)
        
        self.mouse_double = QCheckBox("Double click")
        layout.addWidget(self.mouse_double)
        
        layout.addStretch()
        return widget
    
    def create_mouse_move_params(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        pos_layout = QGridLayout()
        pos_layout.addWidget(QLabel("X:"), 0, 0)
        self.move_x = QSpinBox()
        self.move_x.setRange(-10000, 10000)
        pos_layout.addWidget(self.move_x, 0, 1)
        
        pos_layout.addWidget(QLabel("Y:"), 0, 2)
        self.move_y = QSpinBox()
        self.move_y.setRange(-10000, 10000)
        pos_layout.addWidget(self.move_y, 0, 3)
        
        layout.addLayout(pos_layout)
        
        self.move_relative = QCheckBox("Relative movement")
        layout.addWidget(self.move_relative)
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Duration (ms):"))
        self.move_duration = QSpinBox()
        self.move_duration.setRange(0, 10000)
        self.move_duration.setValue(100)
        speed_layout.addWidget(self.move_duration)
        layout.addLayout(speed_layout)
        
        layout.addStretch()
        return widget
    
    def create_wait_params(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (ms):"))
        self.wait_duration = QSpinBox()
        self.wait_duration.setRange(0, 60000)
        self.wait_duration.setValue(100)
        duration_layout.addWidget(self.wait_duration)
        layout.addLayout(duration_layout)
        
        self.wait_variable = QCheckBox("Use variable duration")
        layout.addWidget(self.wait_variable)
        
        layout.addStretch()
        return widget
    
    def create_file_params(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("File path:"))
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        file_layout.addWidget(self.file_path)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)
        
        layout.addStretch()
        return widget
    
    def create_url_params(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        layout.addWidget(self.url_input)
        
        layout.addStretch()
        return widget
    
    def create_app_params(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Application path:"))
        app_layout = QHBoxLayout()
        self.app_path = QLineEdit()
        app_layout.addWidget(self.app_path)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_application)
        app_layout.addWidget(browse_btn)
        layout.addLayout(app_layout)
        
        layout.addWidget(QLabel("Command line arguments (optional):"))
        self.app_args = QLineEdit()
        self.app_args.setPlaceholderText("e.g., --flag value")
        layout.addWidget(self.app_args)
        
        layout.addStretch()
        return widget
    
    def create_switch_app_params(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Application name or window title:"))
        self.switch_app_name = QLineEdit()
        self.switch_app_name.setPlaceholderText("e.g., 'Chrome', 'notepad.exe'")
        layout.addWidget(self.switch_app_name)
        
        match_layout = QHBoxLayout()
        match_layout.addWidget(QLabel("Match by:"))
        self.switch_match = QComboBox()
        self.switch_match.addItems(["Name", "Title", "Class", "Most Recent"])
        match_layout.addWidget(self.switch_match)
        layout.addLayout(match_layout)
        
        layout.addStretch()
        return widget
    
    def create_script_params(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Script path:"))
        script_layout = QHBoxLayout()
        self.script_path = QLineEdit()
        script_layout.addWidget(self.script_path)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_script)
        script_layout.addWidget(browse_btn)
        layout.addLayout(script_layout)
        
        layout.addWidget(QLabel("Script arguments (optional):"))
        self.script_args = QLineEdit()
        layout.addWidget(self.script_args)
        
        layout.addStretch()
        return widget
    
    def on_type_changed(self, action_type):
        idx = list(self.param_widgets.keys()).index(action_type)
        self.param_stack.setCurrentIndex(idx)
        
    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select File")
        if filename:
            self.file_path.setText(filename)
            
    def browse_application(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Application", "", "Executables (*.exe);;All Files (*.*)")
        if filename:
            self.app_path.setText(filename)
            
    def browse_script(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Script", "", "Scripts (*.py *.bat *.sh);;All Files (*.*)")
        if filename:
            self.script_path.setText(filename)
    
    def load_params(self):
        """Load existing action parameters into the UI"""
        action_type = self.action.action_type
        params = self.action.params
        
        if action_type == "Keyboard Press":
            self.key_input.setText(params.get('key', ''))
            self.key_hold_check.setChecked(params.get('hold', False))
        elif action_type == "Text Paste":
            self.text_input.setPlainText(params.get('text', ''))
            self.variable_check.setChecked(params.get('has_variables', False))
        elif action_type == "Mouse Click":
            self.mouse_button.setCurrentText(params.get('button', 'Left'))
            self.mouse_x.setValue(params.get('x', 0))
            self.mouse_y.setValue(params.get('y', 0))
            self.mouse_relative.setChecked(params.get('relative', False))
            self.mouse_double.setChecked(params.get('double', False))
        elif action_type == "Mouse Move":
            self.move_x.setValue(params.get('x', 0))
            self.move_y.setValue(params.get('y', 0))
            self.move_relative.setChecked(params.get('relative', False))
            self.move_duration.setValue(params.get('duration', 100))
        elif action_type == "Wait":
            self.wait_duration.setValue(params.get('duration', 100))
            self.wait_variable.setChecked(params.get('variable', False))
        elif action_type == "Open File":
            self.file_path.setText(params.get('path', ''))
        elif action_type == "Open URL":
            self.url_input.setText(params.get('url', ''))
        elif action_type == "Open Application":
            self.app_path.setText(params.get('app_path', ''))
            self.app_args.setText(params.get('args', ''))
        elif action_type == "Switch Application":
            self.switch_app_name.setText(params.get('app_name', ''))
            self.switch_match.setCurrentText(params.get('match_by', 'Name'))
        elif action_type == "Run Script":
            self.script_path.setText(params.get('script_path', ''))
            self.script_args.setText(params.get('args', ''))
    
    def get_action(self):
        """Build and return the action from the current UI state"""
        action_type = self.type_combo.currentText()
        params = {}
        
        if action_type == "Keyboard Press":
            params = {
                'key': self.key_input.text(),
                'hold': self.key_hold_check.isChecked()
            }
        elif action_type == "Text Paste":
            params = {
                'text': self.text_input.toPlainText(),
                'has_variables': self.variable_check.isChecked()
            }
        elif action_type == "Mouse Click":
            params = {
                'button': self.mouse_button.currentText(),
                'x': self.mouse_x.value(),
                'y': self.mouse_y.value(),
                'relative': self.mouse_relative.isChecked(),
                'double': self.mouse_double.isChecked()
            }
        elif action_type == "Mouse Move":
            params = {
                'x': self.move_x.value(),
                'y': self.move_y.value(),
                'relative': self.move_relative.isChecked(),
                'duration': self.move_duration.value()
            }
        elif action_type == "Wait":
            params = {
                'duration': self.wait_duration.value(),
                'variable': self.wait_variable.isChecked()
            }
        elif action_type == "Open File":
            params = {'path': self.file_path.text()}
        elif action_type == "Open URL":
            params = {'url': self.url_input.text()}
        elif action_type == "Open Application":
            params = {
                'app_path': self.app_path.text(),
                'args': self.app_args.text()
            }
        elif action_type == "Switch Application":
            params = {
                'app_name': self.switch_app_name.text(),
                'match_by': self.switch_match.currentText()
            }
        elif action_type == "Run Script":
            params = {
                'script_path': self.script_path.text(),
                'args': self.script_args.text()
            }
        
        return MacroAction(action_type, params)


class MacroEditorPanel(GlassWidget):
    """Panel for editing macro details and actions"""
    
    macro_saved = pyqtSignal(Macro)
    
    def __init__(self, parent=None):
        super().__init__(parent, blur_radius=15, opacity=0.2)
        self.current_macro = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Macro Editor")
        title.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Macro name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:", styleSheet="color: #e0e0e0;"))
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Dynamic macro checkbox
        self.dynamic_check = QCheckBox("Dynamic macro (accepts variables)")
        self.dynamic_check.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(self.dynamic_check)
        
        # Actions list
        actions_label = QLabel("Actions:")
        actions_label.setStyleSheet("color: #e0e0e0; font-weight: bold; margin-top: 10px;")
        layout.addWidget(actions_label)
        
        self.actions_list = QListWidget()
        self.actions_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(0, 0, 0, 0.3);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: rgba(100, 150, 255, 0.4);
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        layout.addWidget(self.actions_list)
        
        # Action buttons
        action_btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Action")
        add_btn.clicked.connect(self.add_action)
        self.style_button(add_btn)
        action_btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_action)
        self.style_button(edit_btn)
        action_btn_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_action)
        self.style_button(remove_btn, danger=True)
        action_btn_layout.addWidget(remove_btn)
        
        move_up_btn = QPushButton("↑")
        move_up_btn.clicked.connect(self.move_action_up)
        self.style_button(move_up_btn)
        action_btn_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("↓")
        move_down_btn.clicked.connect(self.move_action_down)
        self.style_button(move_down_btn)
        action_btn_layout.addWidget(move_down_btn)
        
        layout.addLayout(action_btn_layout)
        
        # Save button
        save_btn = QPushButton("Save Macro")
        save_btn.clicked.connect(self.save_macro)
        self.style_button(save_btn, primary=True)
        layout.addWidget(save_btn)
        
    def style_button(self, button, primary=False, danger=False):
        if primary:
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(100, 150, 255, 0.6);
                    color: #ffffff;
                    border: 1px solid rgba(100, 150, 255, 0.8);
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(100, 150, 255, 0.8);
                }
            """)
        elif danger:
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 80, 80, 0.4);
                    color: #ffffff;
                    border: 1px solid rgba(255, 80, 80, 0.6);
                    border-radius: 5px;
                    padding: 8px 15px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 80, 80, 0.6);
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #ffffff;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 5px;
                    padding: 8px 15px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
    
    def load_macro(self, macro):
        """Load a macro into the editor"""
        self.current_macro = macro
        self.name_input.setText(macro.name)
        self.dynamic_check.setChecked(macro.dynamic)
        
        self.actions_list.clear()
        for action in macro.actions:
            item = QListWidgetItem(str(action))
            item.setData(Qt.ItemDataRole.UserRole, action)
            self.actions_list.addItem(item)
    
    def add_action(self):
        dialog = ActionEditorDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            action = dialog.get_action()
            item = QListWidgetItem(str(action))
            item.setData(Qt.ItemDataRole.UserRole, action)
            self.actions_list.addItem(item)
    
    def edit_action(self):
        current_item = self.actions_list.currentItem()
        if not current_item:
            return
            
        action = current_item.data(Qt.ItemDataRole.UserRole)
        dialog = ActionEditorDialog(action, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_action = dialog.get_action()
            current_item.setText(str(new_action))
            current_item.setData(Qt.ItemDataRole.UserRole, new_action)
    
    def remove_action(self):
        current_row = self.actions_list.currentRow()
        if current_row >= 0:
            self.actions_list.takeItem(current_row)
    
    def move_action_up(self):
        current_row = self.actions_list.currentRow()
        if current_row > 0:
            item = self.actions_list.takeItem(current_row)
            self.actions_list.insertItem(current_row - 1, item)
            self.actions_list.setCurrentRow(current_row - 1)
    
    def move_action_down(self):
        current_row = self.actions_list.currentRow()
        if current_row >= 0 and current_row < self.actions_list.count() - 1:
            item = self.actions_list.takeItem(current_row)
            self.actions_list.insertItem(current_row + 1, item)
            self.actions_list.setCurrentRow(current_row + 1)
    
    def save_macro(self):
        actions = []
        for i in range(self.actions_list.count()):
            item = self.actions_list.item(i)
            actions.append(item.data(Qt.ItemDataRole.UserRole))
        
        if self.current_macro:
            self.current_macro.name = self.name_input.text()
            self.current_macro.actions = actions
            self.current_macro.dynamic = self.dynamic_check.isChecked()
        else:
            self.current_macro = Macro(
                name=self.name_input.text(),
                actions=actions,
                dynamic=self.dynamic_check.isChecked()
            )
        
        self.macro_saved.emit(self.current_macro)
    
    def clear(self):
        self.current_macro = None
        self.name_input.clear()
        self.dynamic_check.setChecked(False)
        self.actions_list.clear()


class MacroListPanel(GlassWidget):
    """Panel showing list of all macros"""
    
    macro_selected = pyqtSignal(object)  # Can emit Macro or None
    
    def __init__(self, parent=None):
        super().__init__(parent, blur_radius=15, opacity=0.2)
        self.macros = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title with search
        title = QLabel("Macros")
        title.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search macros...")
        self.search_box.textChanged.connect(self.filter_macros)
        self.search_box.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.search_box)
        
        # Macro list
        self.macro_list = QListWidget()
        self.macro_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(0, 0, 0, 0.3);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 3px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: rgba(100, 150, 255, 0.4);
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.macro_list.itemDoubleClicked.connect(self.on_macro_double_clicked)
        layout.addWidget(self.macro_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        new_btn = QPushButton("New Macro")
        new_btn.clicked.connect(self.new_macro)
        self.style_button(new_btn, primary=True)
        btn_layout.addWidget(new_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_macro)
        self.style_button(edit_btn)
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_macro)
        self.style_button(delete_btn, danger=True)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
    def style_button(self, button, primary=False, danger=False):
        if primary:
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(100, 150, 255, 0.6);
                    color: #ffffff;
                    border: 1px solid rgba(100, 150, 255, 0.8);
                    border-radius: 5px;
                    padding: 10px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(100, 150, 255, 0.8);
                }
            """)
        elif danger:
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 80, 80, 0.4);
                    color: #ffffff;
                    border: 1px solid rgba(255, 80, 80, 0.6);
                    border-radius: 5px;
                    padding: 10px 15px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 80, 80, 0.6);
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #ffffff;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 5px;
                    padding: 10px 15px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
    
    def load_macros(self, macros):
        self.macros = macros
        self.refresh_list()
    
    def refresh_list(self):
        self.macro_list.clear()
        search_text = self.search_box.text().lower()
        
        for macro in self.macros:
            if search_text and search_text not in macro.name.lower():
                continue
                
            item_text = f"{'✓' if macro.enabled else '○'} {macro.name}"
            if macro.dynamic:
                item_text += " 🔄"
            item_text += f" ({len(macro.actions)} actions)"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, macro)
            self.macro_list.addItem(item)
    
    def filter_macros(self):
        self.refresh_list()
    
    def new_macro(self):
        self.macro_selected.emit(None)
    
    def edit_macro(self):
        current_item = self.macro_list.currentItem()
        if current_item:
            macro = current_item.data(Qt.ItemDataRole.UserRole)
            self.macro_selected.emit(macro)
    
    def on_macro_double_clicked(self, item):
        macro = item.data(Qt.ItemDataRole.UserRole)
        self.macro_selected.emit(macro)
    
    def delete_macro(self):
        current_row = self.macro_list.currentRow()
        if current_row >= 0:
            self.macros.pop(current_row)
            self.refresh_list()


class MainWindow(QMainWindow):
    """Main application window with glassmorphism design"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macro Manager")
        self.setGeometry(100, 100, 1400, 800)
        
        # Data
        self.macros = []
        self.config_file = Path.home() / ".macro_manager" / "macros.json"
        self.config_file.parent.mkdir(exist_ok=True)
        
        self.init_ui()
        self.load_macros()
        
    def init_ui(self):
        # Set dark background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e,
                    stop:0.5 #16213e,
                    stop:1 #0f3460
                );
            }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left panel - Macro list
        self.macro_list_panel = MacroListPanel()
        self.macro_list_panel.macro_selected.connect(self.on_macro_selected)
        self.macro_list_panel.setMinimumWidth(350)
        main_layout.addWidget(self.macro_list_panel, 1)
        
        # Right panel - Macro editor
        self.macro_editor_panel = MacroEditorPanel()
        self.macro_editor_panel.macro_saved.connect(self.on_macro_saved)
        self.macro_editor_panel.setMinimumWidth(600)
        main_layout.addWidget(self.macro_editor_panel, 2)
        
    def on_macro_selected(self, macro):
        if macro is None:
            self.macro_editor_panel.clear()
            self.macro_editor_panel.load_macro(Macro())
        else:
            self.macro_editor_panel.load_macro(macro)
    
    def on_macro_saved(self, macro):
        # Add or update macro in list
        existing = False
        for i, m in enumerate(self.macros):
            if m.name == macro.name:
                self.macros[i] = macro
                existing = True
                break
        
        if not existing:
            self.macros.append(macro)
        
        self.macro_list_panel.load_macros(self.macros)
        self.save_macros()
    
    def load_macros(self):
        """Load macros from JSON file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.macros = [Macro.from_dict(m) for m in data]
                    self.macro_list_panel.load_macros(self.macros)
            except Exception as e:
                print(f"Error loading macros: {e}")
    
    def save_macros(self):
        """Save macros to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump([m.to_dict() for m in self.macros], f, indent=2)
        except Exception as e:
            print(f"Error saving macros: {e}")


def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

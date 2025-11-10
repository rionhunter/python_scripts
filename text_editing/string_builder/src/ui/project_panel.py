"""
Project Panel for String Builder Application
Handles project selection and management using PyQt6.
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
                            QComboBox, QFrame, QDialog, QDialogButtonBox, QLineEdit,
                            QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict, Any

class ProjectPanel(QFrame):
    """Panel for project management and selection."""
    
    # Signals
    project_changed = pyqtSignal(str)  # project_id
    
    def __init__(self, parent, project_manager, settings_manager):
        """Initialize project panel."""
        super().__init__(parent)
        
        self.project_manager = project_manager
        self.settings_manager = settings_manager
        
        self.setup_ui()
        self.apply_styling()
        self.refresh()
    
    def setup_ui(self):
        """Setup panel UI."""
        self.setFixedHeight(60)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Project label
        project_label = QLabel("Project:")
        font = QFont(self.settings_manager.appearance.font_family, 12, QFont.Weight.Bold)
        project_label.setFont(font)
        layout.addWidget(project_label)
        
        # Project dropdown
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(200)
        self.project_combo.currentTextChanged.connect(self.on_project_change)
        layout.addWidget(self.project_combo)
        
        # Project info
        self.info_label = QLabel("")
        info_font = QFont(self.settings_manager.appearance.font_family, 9)
        self.info_label.setFont(info_font)
        layout.addWidget(self.info_label)
        
        # Spacer
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        # New project button
        self.new_btn = QPushButton("New")
        self.new_btn.setFixedSize(60, 28)
        self.new_btn.clicked.connect(self.new_project)
        button_layout.addWidget(self.new_btn)
        
        # Rename project button
        self.rename_btn = QPushButton("Rename")
        self.rename_btn.setFixedSize(60, 28)
        self.rename_btn.clicked.connect(self.rename_project)
        button_layout.addWidget(self.rename_btn)
        
        # Delete project button
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setFixedSize(60, 28)
        self.delete_btn.clicked.connect(self.delete_project)
        button_layout.addWidget(self.delete_btn)
        
        layout.addLayout(button_layout)
    
    def apply_styling(self):
        """Apply styling to panel."""
        colors = self.settings_manager.get_color_scheme()
        
        self.setStyleSheet(f"""
        QFrame {{
            background-color: {colors['background']};
            border: 1px solid {colors['secondary']};
            border-radius: 8px;
        }}
        
        QLabel {{
            color: {colors['text']};
            background-color: transparent;
        }}
        
        QComboBox {{
            background-color: white;
            border: 1px solid {colors['primary']};
            border-radius: 4px;
            padding: 4px 8px;
            font-family: "{self.settings_manager.appearance.font_family}";
            font-size: {self.settings_manager.appearance.font_size}px;
        }}
        
        QComboBox:hover {{
            border: 2px solid {colors['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border: none;
            width: 0px;
            height: 0px;
        }}
        
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            border-radius: 4px;
            font-family: "{self.settings_manager.appearance.font_family}";
            font-size: {self.settings_manager.appearance.font_size}px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors['secondary']};
        }}
        """)
        
        # Special styling for delete button
        self.delete_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            color: #ff4444;
            border: 1px solid #ff4444;
            border-radius: 4px;
            font-family: "{self.settings_manager.appearance.font_family}";
            font-size: {self.settings_manager.appearance.font_size}px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #ffdddd;
        }}
        """)
        
        # Special styling for rename button
        self.rename_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            color: {colors['primary']};
            border: 1px solid {colors['primary']};
            border-radius: 4px;
            font-family: "{self.settings_manager.appearance.font_family}";
            font-size: {self.settings_manager.appearance.font_size}px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {colors['background']};
        }}
        """)
    
    def refresh(self):
        """Refresh project list and selection."""
        # Block signals to prevent triggering change event
        self.project_combo.blockSignals(True)
        
        # Clear existing items
        self.project_combo.clear()
        
        # Get project list
        projects = self.project_manager.get_project_list()
        
        # Add projects to combo box
        for project in projects:
            display_name = f"{project['name']} ({project['chunk_count']} chunks)"
            self.project_combo.addItem(display_name, project['id'])
        
        # Set current selection
        current_index = -1
        if self.project_manager.current_project:
            current_project = self.project_manager.current_project
            for i in range(self.project_combo.count()):
                if self.project_combo.itemData(i) == current_project.id:
                    current_index = i
                    break
            
            # Update info label
            self.info_label.setText(f"Modified: {current_project.modified_at[:10]}")
        else:
            self.info_label.setText("")
        
        # Set selection
        if current_index >= 0:
            self.project_combo.setCurrentIndex(current_index)
        
        # Re-enable signals
        self.project_combo.blockSignals(False)
        
        # Update button states
        has_project = self.project_manager.current_project is not None
        self.rename_btn.setEnabled(has_project)
        self.delete_btn.setEnabled(has_project)
    
    def on_project_change(self, text):
        """Handle project selection change."""
        if not text:
            return
        
        # Get selected project ID
        current_index = self.project_combo.currentIndex()
        if current_index < 0:
            return
        
        project_id = self.project_combo.itemData(current_index)
        if project_id and project_id != (self.project_manager.current_project.id if self.project_manager.current_project else None):
            self.project_manager.switch_project(project_id)
            self.refresh()
            self.project_changed.emit(project_id)
    
    def new_project(self):
        """Create a new project."""
        dialog = ProjectDialog(self, "New Project", "", "", self.settings_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, description = dialog.get_result()
            if name:
                project = self.project_manager.create_project(name, description)
                self.refresh()
                self.project_changed.emit(project.id)
    
    def rename_project(self):
        """Rename current project."""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "No Project", "No project selected to rename.")
            return
        
        current = self.project_manager.current_project
        dialog = ProjectDialog(
            self, 
            "Rename Project", 
            current.name, 
            current.description,
            self.settings_manager
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, description = dialog.get_result()
            if name:
                current.name = name
                current.description = description
                self.project_manager.save_current_project()
                self.refresh()
    
    def delete_project(self):
        """Delete current project."""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "No Project", "No project selected to delete.")
            return
        
        current = self.project_manager.current_project
        reply = QMessageBox.question(
            self,
            "Delete Project", 
            f"Are you sure you want to delete the project '{current.name}'?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.project_manager.delete_project(current.id)
            self.refresh()
            self.project_changed.emit("")

class ProjectDialog(QDialog):
    """Dialog for creating/editing projects."""
    
    def __init__(self, parent, title, name="", description="", settings_manager=None):
        """Initialize project dialog."""
        super().__init__(parent)
        
        self.settings_manager = settings_manager
        self.result = None
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(400, 250)
        
        # Center on parent
        if parent:
            parent_geo = parent.geometry()
            self.move(parent_geo.center() - self.rect().center())
        
        self.setup_ui(name, description)
        self.apply_styling()
    
    def setup_ui(self, initial_name, initial_description):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Name field
        name_label = QLabel("Project Name:")
        font = QFont(self.settings_manager.appearance.font_family if self.settings_manager else "Arial", 
                    12, QFont.Weight.Bold)
        name_label.setFont(font)
        layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setText(initial_name)
        self.name_edit.setFixedHeight(32)
        layout.addWidget(self.name_edit)
        
        # Description field
        desc_label = QLabel("Description (optional):")
        desc_label.setFont(font)
        layout.addWidget(desc_label)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlainText(initial_description)
        self.desc_edit.setMaximumHeight(80)
        layout.addWidget(self.desc_edit)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Focus on name field
        self.name_edit.setFocus()
        self.name_edit.selectAll()
    
    def apply_styling(self):
        """Apply styling to dialog."""
        if not self.settings_manager:
            return
        
        colors = self.settings_manager.get_color_scheme()
        
        self.setStyleSheet(f"""
        QDialog {{
            background-color: {colors['background']};
        }}
        
        QLabel {{
            color: {colors['text']};
        }}
        
        QLineEdit, QTextEdit {{
            background-color: white;
            border: 1px solid {colors['primary']};
            border-radius: 4px;
            padding: 8px;
            font-family: "{self.settings_manager.appearance.font_family}";
            font-size: {self.settings_manager.appearance.font_size}px;
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border: 2px solid {colors['primary']};
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
        """)
    
    def accept(self):
        """Accept the dialog with validation."""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Project name cannot be empty.")
            return
        
        description = self.desc_edit.toPlainText().strip()
        self.result = (name, description)
        super().accept()
    
    def get_result(self):
        """Get the dialog result."""
        return self.result

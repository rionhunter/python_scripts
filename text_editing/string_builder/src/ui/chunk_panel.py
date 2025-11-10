"""
Chunk Panel for String Builder Application
Implements advanced drag-and-drop functionality for text chunks using PyQt6.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QTextEdit, QScrollArea, QDialog, QDialogButtonBox,
                            QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QPoint, QRect, QMimeData, pyqtSignal, QTimer
from PyQt6.QtGui import QDrag, QPainter, QFont, QColor, QPalette, QPixmap
from typing import List, Optional, Dict, Any
import uuid

class DraggableChunk(QFrame):
    """A draggable text chunk widget with advanced drag-and-drop."""
    
    # Signals
    chunk_moved = pyqtSignal(str, int)  # chunk_id, new_position
    chunk_deleted = pyqtSignal(str)     # chunk_id
    chunk_edited = pyqtSignal(str, str) # chunk_id, new_content
    
    def __init__(self, chunk, chunk_panel, settings_manager):
        """Initialize draggable chunk."""
        super().__init__()
        
        self.chunk = chunk
        self.chunk_panel = chunk_panel
        self.settings_manager = settings_manager
        
        # Drag state
        self.drag_start_position = QPoint()
        self.is_dragging = False
        
        self.setup_ui()
        self.apply_styling()
    
    def setup_ui(self):
        """Setup the chunk UI."""
        self.setFixedHeight(100)
        self.setFrameStyle(QFrame.Shape.Box)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        # Header with controls
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Position label
        self.position_label = QLabel(f"#{self.chunk.position + 1}")
        self.position_label.setFixedWidth(30)
        font = QFont(self.settings_manager.appearance.font_family, 10, QFont.Weight.Bold)
        self.position_label.setFont(font)
        header_layout.addWidget(self.position_label)
        
        # Drag handle
        self.drag_handle = QLabel("⋮⋮")
        self.drag_handle.setFixedWidth(20)
        self.drag_handle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_handle.setCursor(Qt.CursorShape.OpenHandCursor)
        drag_font = QFont("Arial", 12, QFont.Weight.Bold)
        self.drag_handle.setFont(drag_font)
        header_layout.addWidget(self.drag_handle)
        
        # Spacer
        header_layout.addStretch()
        
        # Edit button
        self.edit_btn = QPushButton("✎")
        self.edit_btn.setFixedSize(25, 20)
        self.edit_btn.clicked.connect(self.edit_chunk)
        header_layout.addWidget(self.edit_btn)
        
        # Delete button
        self.delete_btn = QPushButton("×")
        self.delete_btn.setFixedSize(25, 20)
        self.delete_btn.clicked.connect(self.delete_chunk)
        header_layout.addWidget(self.delete_btn)
        
        layout.addLayout(header_layout)
        
        # Content display
        self.content_display = QTextEdit()
        self.content_display.setPlainText(self.chunk.content)
        self.content_display.setReadOnly(True)
        self.content_display.setMaximumHeight(60)
        self.content_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.content_display.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Enable double-click to edit
        self.content_display.mouseDoubleClickEvent = lambda e: self.edit_chunk()
        
        layout.addWidget(self.content_display)
    
    def apply_styling(self):
        """Apply styling based on settings."""
        colors = self.settings_manager.get_color_scheme()
        
        # Main frame styling
        self.setStyleSheet(f"""
        DraggableChunk {{
            background-color: {colors['secondary']};
            border: 1px solid {colors['primary']};
            border-radius: 8px;
            margin: 2px;
        }}
        
        DraggableChunk:hover {{
            border: 2px solid {colors['primary']};
        }}
        
        QLabel {{
            color: {colors['text']};
            background-color: transparent;
        }}
        
        QPushButton {{
            background-color: transparent;
            border: none;
            color: {colors['primary']};
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {colors['background']};
            border-radius: 3px;
        }}
        
        QTextEdit {{
            background-color: {colors['background']};
            border: none;
            color: {colors['text']};
            font-family: "{self.settings_manager.appearance.font_family}";
            font-size: {self.settings_manager.appearance.font_size}px;
        }}
        """)
        
        # Set delete button to red
        self.delete_btn.setStyleSheet(f"""
        QPushButton {{
            color: #ff4444;
            background-color: transparent;
            border: none;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #ffdddd;
            border-radius: 3px;
        }}
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press for drag initiation."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
            
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for drag operation."""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if not self.drag_start_position:
            return
        
        # Check if drag distance is sufficient
        if ((event.position().toPoint() - self.drag_start_position).manhattanLength() < 
            QApplication.startDragDistance()):
            return
        
        self.start_drag(event)
    
    def start_drag(self, event):
        """Start drag operation."""
        # Create drag object
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Set drag data
        mime_data.setText(f"chunk:{self.chunk.id}")
        drag.setMimeData(mime_data)
        
        # Create drag pixmap (visual representation)
        pixmap = self.grab()
        
        # Make it semi-transparent
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 127))
        painter.end()
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(self.drag_start_position)
        
        # Change cursor
        self.drag_handle.setCursor(Qt.CursorShape.ClosedHandCursor)
        
        # Execute drag
        drop_action = drag.exec(Qt.DropAction.MoveAction)
        
        # Reset cursor
        self.drag_handle.setCursor(Qt.CursorShape.OpenHandCursor)
    
    def edit_chunk(self):
        """Open chunk for editing."""
        dialog = ChunkEditDialog(self, self.chunk, self.settings_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_content = dialog.get_content()
            if new_content != self.chunk.content:
                self.chunk_edited.emit(self.chunk.id, new_content)
    
    def delete_chunk(self):
        """Delete this chunk."""
        reply = QMessageBox.question(
            self, 
            "Delete Chunk", 
            "Are you sure you want to delete this chunk?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.chunk_deleted.emit(self.chunk.id)
    
    def update_position_display(self):
        """Update the position label."""
        self.position_label.setText(f"#{self.chunk.position + 1}")

class ChunkEditDialog(QDialog):
    """Dialog for editing chunk content."""
    
    def __init__(self, parent, chunk, settings_manager):
        """Initialize edit dialog."""
        super().__init__(parent)
        self.chunk = chunk
        self.settings_manager = settings_manager
        
        self.setWindowTitle("Edit Chunk")
        self.setModal(True)
        self.resize(500, 300)
        
        # Center on parent
        if parent:
            parent_geo = parent.geometry()
            self.move(parent_geo.center() - self.rect().center())
        
        self.setup_ui()
        self.apply_styling()
    
    def setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Edit Chunk Content")
        font = QFont(self.settings_manager.appearance.font_family, 14, QFont.Weight.Bold)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Text area
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(self.chunk.content)
        layout.addWidget(self.text_edit)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Focus on text
        self.text_edit.setFocus()
        
        # Shortcuts
        self.text_edit.setTabChangesFocus(False)
    
    def apply_styling(self):
        """Apply styling to dialog."""
        colors = self.settings_manager.get_color_scheme()
        
        self.setStyleSheet(f"""
        QDialog {{
            background-color: {colors['background']};
        }}
        
        QLabel {{
            color: {colors['text']};
        }}
        
        QTextEdit {{
            background-color: white;
            border: 1px solid {colors['primary']};
            border-radius: 4px;
            padding: 8px;
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
        """)
    
    def get_content(self):
        """Get the edited content."""
        return self.text_edit.toPlainText()

class ChunkPanel(QScrollArea):
    """Panel containing all chunks with advanced drag-and-drop functionality."""
    
    def __init__(self, parent, project_manager, settings_manager):
        """Initialize chunk panel."""
        super().__init__(parent)
        
        self.project_manager = project_manager
        self.settings_manager = settings_manager
        
        # Setup scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create main widget
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        
        # Enable drop
        self.setAcceptDrops(True)
        self.main_widget.setAcceptDrops(True)
        
        # Drag and drop state
        self.drop_indicator_line = None
        self.drop_position = -1
        
        self.setup_ui()
        self.apply_styling()
        self.refresh()
    
    def setup_ui(self):
        """Setup panel UI."""
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("String Chunks")
        font = QFont(self.settings_manager.appearance.font_family, 14, QFont.Weight.Bold)
        title_label.setFont(font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add chunk button
        self.add_btn = QPushButton("+ Add Chunk")
        self.add_btn.clicked.connect(self.add_new_chunk)
        header_layout.addWidget(self.add_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # Chunks container
        self.chunks_widget = QWidget()
        self.chunks_layout = QVBoxLayout(self.chunks_widget)
        self.chunks_layout.setContentsMargins(0, 0, 0, 0)
        self.chunks_layout.setSpacing(2)
        
        self.main_layout.addWidget(self.chunks_widget)
        self.main_layout.addStretch()
    
    def apply_styling(self):
        """Apply styling to panel."""
        colors = self.settings_manager.get_color_scheme()
        
        self.setStyleSheet(f"""
        QScrollArea {{
            background-color: {colors['background']};
            border: 1px solid {colors['secondary']};
            border-radius: 8px;
        }}
        
        QWidget {{
            background-color: transparent;
        }}
        
        QLabel {{
            color: {colors['text']};
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
        """)
    
    def refresh(self):
        """Refresh the chunks display."""
        # Clear existing chunks
        for i in reversed(range(self.chunks_layout.count())):
            child = self.chunks_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add chunks
        if self.project_manager.current_project:
            chunks = sorted(self.project_manager.current_project.chunks, 
                          key=lambda c: c.position)
            
            for chunk in chunks:
                chunk_widget = DraggableChunk(
                    chunk,
                    self,
                    self.settings_manager
                )
                
                # Connect signals
                chunk_widget.chunk_moved.connect(self.on_chunk_moved)
                chunk_widget.chunk_deleted.connect(self.on_chunk_deleted)
                chunk_widget.chunk_edited.connect(self.on_chunk_edited)
                
                self.chunks_layout.addWidget(chunk_widget)
        
        # Add empty state if no chunks
        if not self.project_manager.current_project or not self.project_manager.current_project.chunks:
            empty_label = QLabel("No chunks yet. Click 'Add Chunk' to get started!")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont(self.settings_manager.appearance.font_family, 12)
            font.setItalic(True)
            empty_label.setFont(font)
            
            colors = self.settings_manager.get_color_scheme()
            empty_label.setStyleSheet(f"color: {colors['secondary']};")
            
            self.chunks_layout.addWidget(empty_label)
    
    def add_new_chunk(self):
        """Add a new chunk."""
        dialog = ChunkEditDialog(self, type('obj', (object,), {'content': ''})(), self.settings_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            content = dialog.get_content().strip()
            if content:
                self.project_manager.add_chunk(content)
                self.refresh()
                # Update parent status
                if hasattr(self.parent(), 'update_status'):
                    self.parent().update_status()
    
    def on_chunk_moved(self, chunk_id, new_position):
        """Handle chunk moved signal."""
        self.project_manager.move_chunk(chunk_id, new_position)
        self.refresh()
        if hasattr(self.parent(), 'update_status'):
            self.parent().update_status()
    
    def on_chunk_deleted(self, chunk_id):
        """Handle chunk deleted signal."""
        self.project_manager.remove_chunk(chunk_id)
        self.refresh()
        if hasattr(self.parent(), 'update_status'):
            self.parent().update_status()
    
    def on_chunk_edited(self, chunk_id, new_content):
        """Handle chunk edited signal."""
        self.project_manager.update_chunk(chunk_id, new_content)
        self.refresh()
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasText() and event.mimeData().text().startswith("chunk:"):
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """Handle drag move event."""
        if event.mimeData().hasText() and event.mimeData().text().startswith("chunk:"):
            # Calculate drop position
            pos = event.position().toPoint()
            self.calculate_drop_position(pos)
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Handle drop event."""
        if event.mimeData().hasText() and event.mimeData().text().startswith("chunk:"):
            chunk_id = event.mimeData().text().split(":")[1]
            
            if self.drop_position >= 0:
                self.on_chunk_moved(chunk_id, self.drop_position)
            
            event.acceptProposedAction()
    
    def calculate_drop_position(self, pos):
        """Calculate drop position based on mouse position."""
        # This is a simplified version - would need more sophisticated logic
        # for precise drop positioning between chunks
        chunk_count = self.chunks_layout.count()
        if chunk_count == 0:
            self.drop_position = 0
            return
        
        # Find the widget under the mouse
        for i in range(chunk_count):
            widget = self.chunks_layout.itemAt(i).widget()
            if widget and isinstance(widget, DraggableChunk):
                widget_pos = widget.mapFromGlobal(self.mapToGlobal(pos))
                if widget.rect().contains(widget_pos):
                    # Determine if drop should be before or after this widget
                    if widget_pos.y() < widget.height() // 2:
                        self.drop_position = i
                    else:
                        self.drop_position = i + 1
                    return
        
        # Default to end
        self.drop_position = chunk_count

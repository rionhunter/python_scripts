"""Main entry point for the PyQt6 Text/Markdown File Compiler."""

import sys
import os

# Add the current directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import PyQt6
        return True
    except ImportError:
        print("Error: PyQt6 is not installed.")
        print("Please install it using: pip install PyQt6>=6.4.0")
        return False

def main():
    """Main application entry point."""
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    # Import PyQt6 modules after dependency check
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    from gui.main_window import MainWindow


def main():
    """Main application entry point."""
def main():
    """Main application entry point."""
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    # Import PyQt6 modules after dependency check
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    from gui.main_window import MainWindow
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Text File Compiler")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TextFileCompiler")
    app.setOrganizationDomain("textfilecompiler.local")
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Enable high DPI support
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    # Create and show main window
    try:
        window = MainWindow()
        window.show()
        
        # Start the event loop
        return app.exec()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
"""Main entry point for the PyQt6 Text/Markdown File Compiler."""

import argparse
import importlib
import os
import sys

# Add the current directory to the Python path for imports.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_dependencies():
    """Check that required runtime dependencies are available."""
    # Allow tests and CI to bypass dependency checks when explicitly requested
    if os.environ.get("TFC_SKIP_DEP_CHECK"):
        return True
    required_modules = {
        "PyQt6": "pip install PyQt6>=6.4.0",
        "chardet": "pip install chardet",
    }

    missing_modules = []
    for module_name, install_hint in required_modules.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing_modules.append((module_name, install_hint))

    if not missing_modules:
        return True

    for module_name, install_hint in missing_modules:
        print(f"Error: {module_name} is not installed.")
        print(f"Please install it using: {install_hint}")

    return False


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Launch the Text File Compiler GUI.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate imports and create the main window without entering the event loop.",
    )
    parser.add_argument(
        "--offscreen",
        action="store_true",
        help="Force Qt to use the offscreen platform. Useful for automated smoke tests.",
    )
    return parser.parse_args(argv)


def configure_qt_font_directory():
    """Set a usable Qt font directory when PyQt6's default packaged path is missing."""
    if os.environ.get("QT_QPA_FONTDIR"):
        return

    candidate_dirs = []
    try:
        pyqt6_module = importlib.import_module("PyQt6")
        pyqt6_root = os.path.dirname(pyqt6_module.__file__)
        candidate_dirs.extend(
            [
                os.path.join(pyqt6_root, "Qt6", "lib", "fonts"),
                os.path.join(pyqt6_root, "Qt6", "fonts"),
            ]
        )
    except Exception:
        pass

    candidate_dirs.extend(
        [
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts"),
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            "/Library/Fonts",
            os.path.expanduser("~/.fonts"),
        ]
    )

    for font_dir in candidate_dirs:
        if font_dir and os.path.isdir(font_dir):
            os.environ["QT_QPA_FONTDIR"] = font_dir
            return


def create_application(offscreen=False):
    """Create and configure the QApplication instance."""
    if offscreen and "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"

    configure_qt_font_directory()

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QFont

    app = QApplication(sys.argv)
    app.setApplicationName("Text File Compiler")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TextFileCompiler")
    app.setOrganizationDomain("textfilecompiler.local")
    app.setFont(QFont("Segoe UI", 10))
    return app


def resolve_main_window_class():
    """Import and return the main window class."""
    from gui.main_window import MainWindow

    return MainWindow


def run_startup_check(offscreen=False):
    """Smoke-test application startup without starting the event loop."""
    app = create_application(offscreen=offscreen)
    main_window_class = resolve_main_window_class()
    window = main_window_class()
    window.close()
    app.quit()
    return 0


def main(argv=None):
    """Main application entry point."""
    args = parse_args(argv)

    if not check_dependencies():
        return 1

    try:
        if args.check:
            return run_startup_check(offscreen=args.offscreen)

        app = create_application(offscreen=args.offscreen)
        main_window_class = resolve_main_window_class()
        window = main_window_class()
        window.show()
        return app.exec()
    except Exception as error:
        print(f"Error starting application: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
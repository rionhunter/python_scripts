#!/usr/bin/env python3
"""
Demo script to showcase the text file compiler functionality.

This script demonstrates how to use the core compilation features
without requiring the GUI.
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.compiler import Compiler
from settings.config import ProjectConfig


def create_demo_compilation():
    """Create a demonstration compilation."""
    print("PyQt6 Text File Compiler - Demo Compilation")
    print("=" * 50)
    
    # Get the demo files
    demo_dir = os.path.join(os.path.dirname(__file__), "demo_files")
    demo_files = []
    
    for filename in ["sample_python.py", "sample_markdown.md", "config.json", "styles.css"]:
        file_path = os.path.join(demo_dir, filename)
        if os.path.exists(file_path):
            demo_files.append(file_path)
    
    if not demo_files:
        print("❌ No demo files found. Please ensure demo_files directory exists.")
        return
    
    print(f"Found {len(demo_files)} demo files:")
    for file_path in demo_files:
        print(f"  - {os.path.basename(file_path)}")
    print()
    
    # Create project configuration
    project_config = {
        'name': 'PyQt6 Text File Compiler Demo',
        'description': 'Demonstration of the enhanced text file compiler with PyQt6 GUI features',
        'output_settings': {
            'include_file_names': True,
            'include_file_tree': True
        }
    }
    
    # Compile the files
    print("Compiling files...")
    compiler = Compiler()
    
    try:
        result = compiler.compile_files(demo_files, project_config)
        
        # Save the output
        output_file = "demo_compilation_output.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        
        print(f"✅ Compilation completed! Output saved to: {output_file}")
        print()
        
        # Show statistics
        stats = compiler.get_compilation_stats(demo_files)
        print("Compilation Statistics:")
        print(f"  📁 Total files: {stats['total_files']}")
        print(f"  📄 Text files: {stats['text_files']}")
        print(f"  🔧 Binary files: {stats['binary_files']}")
        print(f"  📊 Total size: {stats['total_size']} bytes")
        print(f"  🏷️ File types: {', '.join(stats['extensions'].keys())}")
        print()
        
        # Show preview of output
        print("Output Preview (first 500 characters):")
        print("-" * 50)
        print(result[:500] + "..." if len(result) > 500 else result)
        print("-" * 50)
        print()
        
        print("🎉 Demo completed successfully!")
        print()
        print("To see the full functionality:")
        print("1. Install PyQt6: pip install PyQt6>=6.4.0")
        print("2. Run the GUI: python main.py")
        print("3. Create a new project and add these demo files")
        print("4. Experience all the enhanced GUI features!")
        
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        import traceback
        traceback.print_exc()


def show_feature_summary():
    """Show a summary of all implemented features."""
    print("\n" + "=" * 60)
    print("PYQT6 TEXT FILE COMPILER - FEATURE SUMMARY")
    print("=" * 60)
    
    features = {
        "✅ CORE FUNCTIONALITY": [
            "File compilation with syntax highlighting",
            "Project files for different contexts/collections",
            "Built-in file browser with persistent location",
            "Support for 20+ file types",
            "File tree generation",
            "Encoding detection and handling"
        ],
        "✅ GUI ENHANCEMENTS": [
            "Frameless design",
            "Drag to move (Right-click + drag)",
            "Context menu (Right-click release after no drag)",
            "Resize from center (Shift + Right-click)",
            "Resize panel below mouse (Ctrl + Shift + Right-click)",
            "Zoom in/out (Shift + Middle-click drag up/down)",
            "Pan when zoomed (Middle-click drag)",
            "Scale window and contents (Ctrl + Shift + Middle-click drag)",
            "Window position persistence",
            "Close with Escape key"
        ],
        "✅ AESTHETIC FEATURES": [
            "Frosty glass effect with translucent background",
            "Earthy pastel colors with forest green trim",
            "Rounded corners throughout",
            "Healthy margins for comfortable viewing",
            "Gradient outline that reacts to window position",
            "Modern typography (Segoe UI font family)",
            "Smooth animations and transitions"
        ],
        "✅ PROJECT MANAGEMENT": [
            "Save/load project files locally",
            "Persistent file browser location per project",
            "Project-specific settings",
            "File list with drag & drop reordering",
            "Auto-save functionality"
        ]
    }
    
    for category, items in features.items():
        print(f"\n{category}")
        for item in items:
            print(f"  • {item}")
    
    print("\n" + "=" * 60)
    print("All requested features have been implemented!")
    print("=" * 60)


if __name__ == "__main__":
    create_demo_compilation()
    show_feature_summary()
# PyQt6 Text/Markdown File Compiler

A modern, feature-rich PyQt6 application for compiling text and markdown files with advanced GUI features and project management capabilities.

## Features

### Core Functionality
- **File Compilation**: Combine multiple text/markdown files into a single output
- **Project Management**: Create, save, and load project files for different contexts
- **Built-in File Browser**: Navigate and select files with persistent location per project
- **Syntax Highlighting**: Automatic language detection for code files
- **File Tree Generation**: Include directory structure in compiled output

### Advanced GUI Features
- **Frameless Design**: Modern, clean interface without traditional window borders
- **Drag to Move**: Right-click + drag to move the window
- **Context Menu**: Right-click release (after no drag) opens dropdown settings
- **Window Resizing**: 
  - Shift + Right-click: Resize from center based on cursor vector
  - Ctrl + Shift + Right-click: Resize panel below mouse
- **Zoom & Pan**: 
  - Shift + Middle-click drag up/down: Zoom in/out
  - Middle-click drag: Pan when zoomed
- **Scaling**: Ctrl + Shift + Middle-click drag up/down: Scale window frame and contents
- **Persistence**: Application remembers window position and settings between sessions
- **Close**: Escape key to close application

### Aesthetic Design
- **Frosty Glass Effect**: Translucent background with blur effects
- **Earthy Pastel Colors**: Soothing color palette with forest green trim
- **Rounded Corners**: Modern UI with smooth, rounded elements
- **Healthy Margins**: Proper spacing for comfortable viewing
- **Gradient Outline**: Dynamic outline that reacts to window's screen position
- **Modern Typography**: Clean, readable fonts throughout

## Installation

1. Ensure you have Python 3.8+ installed
2. Install the required dependencies:
   ```bash
   pip install PyQt6>=6.4.0
   ```

## Usage

### Running the Application
```bash
cd text_file_compiler
python main.py
```

### Creating a New Project
1. Click "New" in the project controls
2. Choose a location and name for your project file
3. The project will be automatically loaded

### Adding Files
- **Via File Browser**: 
  1. Navigate to the "Browse" tab
  2. Browse to your desired directory
  3. Double-click files to add them to the project
- **Via File Dialog**: 
  1. Switch to the "Files" tab
  2. Click "Add File" to open a file selection dialog

### Compiling Files
1. Select the files you want to include in the compilation
2. Configure output options (include file names, file tree)
3. Click "Compile" to generate the combined output
4. Use "Copy to Clipboard" or "Save Output" to export results

### Project Management
- **Save Project**: Saves current file list and settings
- **Load Project**: Opens an existing project file
- Projects automatically remember:
  - File list and order
  - File browser location
  - Output settings

## Keyboard Shortcuts

- **Escape**: Close application
- **Right-click + Drag**: Move window
- **Shift + Right-click**: Resize from center
- **Ctrl + Shift + Right-click**: Resize panel
- **Shift + Middle-click drag**: Zoom in/out
- **Ctrl + Shift + Middle-click drag**: Scale interface

## File Support

The application supports a wide variety of text file formats:
- **Code Files**: .py, .js, .java, .cpp, .cs, .php, .rb, .go, etc.
- **Markup**: .md, .html, .xml, .rst, .tex
- **Configuration**: .json, .yaml, .ini, .cfg, .conf
- **Scripts**: .sh, .bat, .ps1
- **Data**: .csv, .sql
- **General Text**: .txt, .log

## Configuration

Settings are automatically saved and include:
- Window position and size
- Last used directories
- Current project
- Zoom and scale levels

Configuration files are stored in:
- **Windows**: `%APPDATA%/TextFileCompiler/`
- **macOS**: `~/Library/Preferences/TextFileCompiler/`
- **Linux**: `~/.config/TextFileCompiler/`

## Project Structure

```
text_file_compiler/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md              # Documentation
├── core/
│   ├── compiler.py        # File compilation logic
│   └── file_processor.py  # File processing utilities
├── gui/
│   └── main_window.py     # Main GUI window
└── settings/
    └── config.py          # Settings management
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## System Requirements

- Python 3.8 or higher
- PyQt6 6.4.0 or higher
- Operating System: Windows 10+, macOS 10.14+, or Linux with X11/Wayland

## Troubleshooting

### Application Won't Start
- Ensure PyQt6 is properly installed: `pip install --upgrade PyQt6`
- Check Python version: `python --version`

### Files Not Loading
- Verify file paths are accessible
- Check file permissions
- Try with a simple text file first

### Performance Issues
- Large files (>10MB) may take time to process
- Consider splitting very large projects
- Close other applications to free memory

## Future Enhancements

- Plugin system for custom file processors
- Themes and customizable color schemes
- Export to various formats (PDF, HTML, etc.)
- Real-time collaboration features
- Version control integration
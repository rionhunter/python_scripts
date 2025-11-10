# String Builder Application

A sophisticated Python application for building strings with persistent chunks that can be rearranged using drag and drop functionality. Features project management, frameless window design with custom controls, and professional styling.

## Features

### Core Functionality
- **Persistent String Chunks**: Create and manage text chunks that persist between sessions
- **Drag and Drop Interface**: Intuitive drag-and-drop functionality for rearranging chunks  
- **Project Management**: Switch between different projects/profiles with isolated chunk collections
- **Settings Management**: Comprehensive settings panel for customizing appearance and behavior

### User Interface
- **Frameless Window**: Modern frameless window design with custom title bar controls
- **Professional Styling**: Clean, responsive design with proper PyQt6 integration
- **Custom Controls**: Minimize, maximize, and close buttons with hover effects
- **Responsive Design**: Adaptive layout that works across different screen sizes

### Advanced Features
- **Auto-save**: Automatic saving of projects and settings
- **Project Switching**: Quick switching between different projects
- **Customizable Appearance**: Configurable colors, fonts, and layout settings
- **Data Persistence**: All data stored in JSON format for easy backup and sharing

## Requirements

- Python 3.8 or higher
- PyQt6 6.5.0+

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
4. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Activate your virtual environment
2. Run the application:
   ```bash
   python main.py
   ```

### Basic Operations

1. **Creating Chunks**: Use the chunk panel to add new text chunks
2. **Editing Chunks**: Double-click on any chunk to edit its content
3. **Rearranging**: Drag and drop chunks to reorder them
4. **Projects**: Use the project panel to create, switch, and manage projects
5. **Settings**: Access the settings panel to customize appearance and behavior

## Project Structure

```
string_builder/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── data/                  # Data storage directory
│   ├── projects/          # Project files
│   └── settings.json      # Application settings
└── src/                   # Source code
    ├── __init__.py
    ├── core/              # Core business logic
    │   ├── __init__.py
    │   ├── project_manager.py    # Project management
    │   └── settings_manager.py   # Settings persistence
    └── ui/                # User interface components
        ├── __init__.py
        ├── main_window.py         # Main frameless window
        ├── chunk_panel.py         # Drag-and-drop chunk interface
        ├── project_panel.py       # Project management UI
        └── settings_panel.py      # Settings configuration UI
```

## Configuration

The application automatically creates a `data/settings.json` file to store user preferences. This includes:

- Window position and size
- Color scheme preferences  
- Font settings
- Auto-save configuration
- Default project formatting options

## Data Storage

- **Projects**: Stored as JSON files in `data/projects/`
- **Settings**: Stored in `data/settings.json`
- **Backups**: Automatic backups created during save operations

## Development

This application is built using:
- **PyQt6**: Modern cross-platform GUI framework
- **Python 3.8+**: Core runtime
- **JSON**: Data serialization and storage
- **Modular Architecture**: Separated UI and business logic

### Adding Features

1. Core functionality goes in `src/core/`
2. UI components go in `src/ui/`
3. Follow the existing patterns for data persistence
4. Use the settings manager for user preferences

## Troubleshooting

### Common Issues

1. **Application won't start**: Ensure PyQt6 is installed (`pip install PyQt6`)
2. **Settings not saving**: Check write permissions in the `data/` directory
3. **Drag and drop not working**: Verify PyQt6 is properly installed
4. **High DPI issues**: PyQt6 handles this automatically on modern systems

## Version History

- **v1.0**: Initial release with PyQt6 implementation
  - Frameless window design
  - Advanced drag-and-drop functionality
  - Comprehensive settings management
  - Project-based organization

## License

This project is provided as-is for educational and personal use.

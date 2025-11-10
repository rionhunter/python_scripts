# Macro Manager

A modern, sleek macro automation application with glassmorphism UI design. Create and execute complex multi-step macros triggered by multiple input devices including secondary keyboards, game controllers, MIDI devices, text commands, and AI-powered voice dictation.

## Features

### 🎨 Modern UI
- **Glassmorphism Design**: Blurred glass background with slight darkening and light fonts
- **Minimal Interface**: Expands only when needed
- **Smooth Animations**: Professional look and feel
- **Dark Theme**: Easy on the eyes for extended use

### 🎮 Multi-Device Input Support
- **Secondary Keyboards**: Capture input from additional keyboards
- **Game Controllers**: Use controller buttons and axes as triggers
- **MIDI Devices**: Trigger macros from MIDI controllers
- **Text Commands**: Execute macros via typed commands
- **AI Dictation**: Voice-controlled macro execution with natural language processing

### ⚡ Powerful Macro Actions
- **Keyboard**: Press keys, hotkey combinations, hold keys
- **Text Paste**: Insert text with variable substitution
- **Mouse**: Click, double-click, move cursor (absolute or relative)
- **Wait**: Delays with fixed or variable duration
- **File Operations**: Open files with default applications
- **Web**: Open URLs in browser
- **Applications**: Launch apps with command-line arguments
- **Window Management**: Switch between applications
- **Scripts**: Execute Python, Batch, or Shell scripts

### 🔄 Dynamic Macros
Create macros that accept runtime variables:
- "delete last 3 words"
- "wait 500 milliseconds"
- "repeat 5 times"
- "select 10 lines"
- "move 100 pixels right"

### 💾 Configuration
- JSON-based settings storage
- Device configurations
- Trigger mappings
- Import/Export configurations

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Install Dependencies

```powershell
pip install -r requirements.txt
```

### Optional Dependencies

For specific features, you may need to install additional components:

**Windows users:**
- PyAudio for voice recognition: Download from [unofficial binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

**Linux users:**
```bash
# For voice recognition
sudo apt-get install portaudio19-dev python3-pyaudio

# For window switching
sudo apt-get install wmctrl

# For MIDI support
sudo apt-get install libasound2-dev libjack-dev
```

**macOS users:**
```bash
# For voice recognition
brew install portaudio

# For MIDI support
brew install jack
```

## Quick Start

### Basic Usage

1. **Launch the application:**
```powershell
python macro_manager.py
```

2. **Create a macro:**
   - Click "New Macro" in the left panel
   - Give it a name
   - Click "Add Action" to add steps
   - Configure each action
   - Click "Save Macro"

3. **Execute a macro:**
   - Double-click the macro in the list
   - Or assign it a hotkey trigger

### Example Macros

**Simple Text Paste:**
```
1. Text Paste: "Hello, World!"
```

**Open Website:**
```
1. Open URL: https://github.com
```

**Complex Workflow:**
```
1. Open Application: C:\Program Files\Notepad++\notepad++.exe
2. Wait: 1000ms
3. Keyboard Press: ctrl+n
4. Text Paste: "# New Document"
5. Keyboard Press: enter
```

**Dynamic Macro:**
Enable "Dynamic macro" checkbox and create actions with variables:
```
1. Text Paste: {text_content} (with variables enabled)
2. Wait: {duration}ms (with variable duration enabled)
```

Then execute with: "type 'Hello' and wait 500 milliseconds"

## Configuration

### Settings Location
All configuration files are stored in:
- Windows: `C:\Users\<username>\.macro_manager\`
- macOS/Linux: `~/.macro_manager/`

### Files
- `settings.json` - Application settings
- `macros.json` - Macro definitions
- `devices.json` - Input device configurations
- `triggers.json` - Trigger mappings

### Key Settings

**UI Settings:**
```json
{
  "ui": {
    "theme": "dark",
    "glass_opacity": 0.15,
    "blur_radius": 20,
    "window_width": 1400,
    "window_height": 800
  }
}
```

**Execution Settings:**
```json
{
  "execution": {
    "typing_speed": 50,
    "mouse_movement_speed": 1.0,
    "log_execution": true
  }
}
```

**Global Hotkeys:**
```json
{
  "hotkeys": {
    "show_hide": "ctrl+shift+m",
    "execute_last": "ctrl+shift+e",
    "stop_execution": "ctrl+shift+s"
  }
}
```

## Input Devices

### Keyboard
Captures keyboard input for macro triggers. Supports hotkey combinations.

### Game Controllers
Connect a game controller and use buttons/axes as triggers:
```python
# Configure controller index (0 = first controller)
config.set("input_devices.game_controller.controller_index", 0)
config.set("input_devices.game_controller.enabled", True)
```

### MIDI Devices
Use MIDI controllers to trigger macros. Supports note on/off and control changes.
```python
# List available MIDI devices
import mido
print(mido.get_input_names())

# Enable MIDI
config.set("input_devices.midi.enabled", True)
config.set("input_devices.midi.device_name", "Your MIDI Device")
```

### Voice Commands
Enable AI-powered voice recognition:
```python
config.set("input_devices.voice.enabled", True)
config.set("input_devices.voice.language", "en-US")
```

Then speak commands like:
- "type 'meeting notes'"
- "open notepad"
- "click at 500, 300"

## Dynamic Macros

Dynamic macros parse natural language commands and extract variables at runtime.

### Supported Commands

**Delete Words:**
- "delete last 3 words"
- "remove last 5 words"

**Timing:**
- "wait 500 milliseconds"
- "wait 2 seconds"
- "pause for 1000 ms"

**Typing:**
- "type 'Hello World'"
- "write 'Test message'"

**Keys:**
- "press enter"
- "hit escape"

**Mouse:**
- "click at 100, 200"
- "click left"
- "click right"

**Applications:**
- "open notepad"
- "launch chrome"

**Repetition:**
- "repeat 5 times"

### Creating Dynamic Macros

1. Create a new macro
2. Check "Dynamic macro (accepts variables)"
3. Add actions with variable placeholders like `{count}`, `{duration}`, `{text}`
4. Execute with natural language input

## Advanced Usage

### Scripting Integration

Run external scripts as macro actions:
```python
action = MacroAction("Run Script", {
    "script_path": "C:\\scripts\\process_data.py",
    "args": "--input data.csv"
})
```

### Variable Substitution

Use variables in text paste actions:
```python
action = MacroAction("Text Paste", {
    "text": "Hello {name}, you have {count} messages",
    "has_variables": True
})

# Execute with variables
executor.execute_action("Text Paste", action.params, {
    "name": "John",
    "count": 5
})
```

### Custom Input Handlers

Create custom input device handlers:
```python
from input_handler import InputDevice, InputEvent, InputDeviceType

class CustomDevice(InputDevice):
    def __init__(self, device_id):
        super().__init__(device_id, InputDeviceType.KEYBOARD)
    
    def start(self):
        # Your listening logic
        pass
    
    def stop(self):
        # Cleanup
        pass
```

## Development

### Project Structure
```
macro_manager/
├── macro_manager.py       # Main UI application
├── input_handler.py       # Multi-device input system
├── macro_executor.py      # Action execution engine
├── dynamic_macros.py      # Dynamic macro parsing
├── config_manager.py      # Configuration management
├── requirements.txt       # Dependencies
└── README.md             # This file
```

### Architecture

**UI Layer (macro_manager.py):**
- PyQt6-based glassmorphism interface
- Macro list and editor panels
- Action configuration dialogs

**Input Layer (input_handler.py):**
- Device abstraction
- Event routing
- Multi-device support

**Execution Layer (macro_executor.py):**
- Action execution
- Platform-specific implementations
- Error handling

**Dynamic Layer (dynamic_macros.py):**
- Natural language parsing
- Variable extraction
- Template substitution

**Config Layer (config_manager.py):**
- Settings persistence
- Device configurations
- Trigger mappings

## Troubleshooting

### Keyboard/Mouse automation not working
- **Windows**: Run as administrator
- **Linux**: Add user to input group: `sudo usermod -a -G input $USER`
- **macOS**: Grant accessibility permissions in System Preferences

### Voice recognition not working
- Check microphone is connected and working
- Install PyAudio: `pip install pyaudio`
- For Windows, may need to download .whl file

### MIDI device not detected
- Install python-rtmidi: `pip install python-rtmidi`
- Check device is connected: `python -c "import mido; print(mido.get_input_names())"`

### Game controller not recognized
- Install pygame: `pip install pygame`
- Test controller: `python -c "import pygame; pygame.init(); pygame.joystick.init(); print(pygame.joystick.get_count())"`

## Security Considerations

⚠️ **Important**: This application can execute system commands and scripts. 

- Only use trusted macro definitions
- Be careful when importing configurations
- Review script paths before execution
- Consider running in a sandboxed environment for untrusted macros

## Contributing

Contributions are welcome! Areas for improvement:
- Additional input device types
- More action types
- UI themes and customization
- Cloud sync for macros
- Macro marketplace/sharing
- Visual macro recorder
- Advanced scripting engine

## License

MIT License - See LICENSE file for details

## Acknowledgments

- PyQt6 for the UI framework
- All open-source libraries used in this project
- The automation community for inspiration

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Made with ❤️ for automation enthusiasts**

# Macro Manager - Project Overview

## 📁 Project Structure

```
macro_manager/
│
├── 🎨 Core Application
│   ├── macro_manager.py          # Main UI with glassmorphism design
│   ├── macro_executor.py         # Action execution engine
│   ├── input_handler.py          # Multi-device input system
│   ├── dynamic_macros.py         # Natural language parsing
│   └── config_manager.py         # Settings & configuration
│
├── 📋 Documentation
│   ├── README.md                 # Full documentation
│   ├── QUICKSTART.md            # Quick start guide
│   └── LICENSE                   # MIT License
│
├── 🚀 Utilities
│   ├── launch.bat               # Windows launcher
│   ├── demo.py                  # Examples & demonstrations
│   └── requirements.txt         # Python dependencies
│
└── 💾 Data (auto-created)
    └── ~/.macro_manager/
        ├── settings.json        # App settings
        ├── macros.json         # Saved macros
        ├── devices.json        # Device configs
        └── triggers.json       # Trigger mappings
```

## 🎯 Key Features

### 1. Modern Glassmorphism UI
- Blurred glass background with darkening overlay
- Light fonts for contrast
- Smooth animations and transitions
- Minimal, expandable interface

### 2. Multi-Device Input Support
```
⌨️  Keyboard        → Hotkeys, key combinations
🎮 Game Controller  → Buttons, axes, D-pad
🎹 MIDI Device      → Notes, control changes
💬 Text Commands    → Typed macro triggers
🎤 AI Dictation     → Voice-controlled execution
```

### 3. Comprehensive Action Types
```
📝 Text Paste           → Insert text with variables
⌨️  Keyboard Press      → Keys and hotkey combos
🖱️  Mouse Click         → Click, double-click, positioning
↔️  Mouse Move          → Absolute or relative movement
⏱️  Wait                → Fixed or variable delays
📂 Open File           → Launch files with default app
🌐 Open URL            → Open websites
🚀 Open Application    → Launch apps with arguments
🔄 Switch Application  → Focus existing windows
📜 Run Script          → Execute Python/Batch/Shell scripts
```

### 4. Dynamic Macros
Natural language parsing:
- "delete last 3 words"
- "wait 500 milliseconds"
- "type 'Hello World'"
- "click at 100, 200"
- "open notepad"

### 5. Variable Substitution
Templates with runtime values:
```python
"Hello {name}, you have {count} messages"
# Execute with: {"name": "John", "count": 5}
# Result: "Hello John, you have 5 messages"
```

## 🔧 Technical Architecture

### Layer 1: Presentation (UI)
**File:** `macro_manager.py`
- PyQt6-based interface
- Glass widget components
- Macro list & editor panels
- Action configuration dialogs

### Layer 2: Input Processing
**File:** `input_handler.py`
- Device abstraction (InputDevice base class)
- Event routing (InputManager)
- Multi-threading for concurrent device listening
- Callbacks for event handling

### Layer 3: Execution Engine
**File:** `macro_executor.py`
- Platform-specific implementations
- Action execution with error handling
- Variable substitution
- Macro sequencing

### Layer 4: Intelligence
**File:** `dynamic_macros.py`
- Natural language parsing
- Regex pattern matching
- Variable extraction
- Template generation

### Layer 5: Configuration
**File:** `config_manager.py`
- JSON-based persistence
- Settings hierarchy
- Import/export functionality
- Default value management

## 🎨 UI Design Philosophy

### Glassmorphism Elements
```
Background:
  ├─ Gradient: #1a1a2e → #16213e → #0f3460
  └─ Glass panels with 15% opacity

Glass Effect:
  ├─ Blur radius: 20px
  ├─ Dark background: rgba(0, 0, 0, 0.15)
  ├─ Border: rgba(255, 255, 255, 0.3)
  └─ Subtle gradient overlay

Typography:
  ├─ Font: Segoe UI
  ├─ Colors: #ffffff (primary), #e0e0e0 (secondary)
  └─ Sizes: 24px (titles), 14px (content)

Buttons:
  ├─ Primary: rgba(100, 150, 255, 0.6)
  ├─ Normal: rgba(255, 255, 255, 0.1)
  └─ Danger: rgba(255, 80, 80, 0.4)
```

### Layout Structure
```
┌─────────────────────────────────────────────────┐
│  Macro Manager                           [ _ □ X ]│
├──────────────┬──────────────────────────────────┤
│              │                                   │
│  📋 Macros   │  📝 Macro Editor                 │
│              │                                   │
│  [Search...] │  Name: ________________          │
│              │                                   │
│  • Macro 1   │  ☐ Dynamic macro                 │
│  • Macro 2   │                                   │
│  • Macro 3   │  Actions:                        │
│    ...       │  ┌──────────────────────────┐   │
│              │  │ 1. Press: ctrl+c         │   │
│  [New Macro] │  │ 2. Wait: 100ms           │   │
│  [Edit]      │  │ 3. Paste: {text}         │   │
│  [Delete]    │  └──────────────────────────┘   │
│              │                                   │
│              │  [Add] [Edit] [Remove] [↑] [↓]  │
│              │                                   │
│              │  [Save Macro]                    │
│              │                                   │
└──────────────┴──────────────────────────────────┘
```

## 🔌 Dependencies

### Required
- **PyQt6** - Modern UI framework
- **pyperclip** - Clipboard operations
- **keyboard** - Keyboard automation
- **pyautogui** - Mouse automation

### Optional (by feature)
- **pygame** - Game controller support
- **mido** - MIDI device support
- **SpeechRecognition** - Voice dictation
- **pygetwindow** - Window management (Windows)

## 🚀 Getting Started

### Installation
```powershell
# 1. Clone or download the project
cd macro_manager

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python macro_manager.py
# or
launch.bat
```

### First Macro
```python
1. Click "New Macro"
2. Name it "Hello World"
3. Add action: Text Paste → "Hello World!"
4. Save
5. Double-click to execute
```

## 📊 Performance Characteristics

### Startup Time
- Cold start: ~2-3 seconds
- Warm start: ~1 second

### Memory Usage
- Base: ~50-80 MB
- With input devices: +10-20 MB per device
- Per macro: ~1-5 KB

### Execution Speed
- Keyboard actions: ~10ms
- Mouse actions: ~20ms
- Text paste: ~50ms (depends on length)
- Application launch: Variable (OS dependent)

## 🔐 Security Considerations

### Risks
- ⚠️ Can execute arbitrary commands
- ⚠️ Can simulate user input
- ⚠️ Can access files and applications

### Mitigations
- Review macros before execution
- Sandbox untrusted macros
- Audit imported configurations
- Use version control for macro files
- Limit script execution permissions

## 🎯 Use Cases

### Productivity
- Email templates and signatures
- Code snippet insertion
- Document formatting
- File organization

### Development
- Build and deploy workflows
- Testing automation
- Environment setup
- Git operations

### Content Creation
- Video editing shortcuts
- Audio processing workflows
- Image manipulation
- Social media posting

### Accessibility
- Custom input mappings
- Voice-controlled workflows
- Simplified complex operations
- Assistive automation

## 🔮 Future Enhancements

### Planned Features
- [ ] Visual macro recorder
- [ ] Cloud sync
- [ ] Macro marketplace
- [ ] Advanced scripting (Lua/Python embedded)
- [ ] Conditional logic in macros
- [ ] Loop constructs
- [ ] Screen recognition triggers
- [ ] OCR integration
- [ ] System tray integration
- [ ] Statistics & analytics

### API Expansion
- [ ] REST API for remote control
- [ ] Plugin system
- [ ] Macro scheduling
- [ ] Event-based triggers
- [ ] Integration with automation tools

## 📞 Support & Community

### Getting Help
1. Check QUICKSTART.md for basics
2. Review README.md for detailed docs
3. Run demo.py for examples
4. Check GitHub issues

### Contributing
- Fork the repository
- Create feature branch
- Submit pull request
- Follow code style
- Add tests for new features

## 📈 Version History

### v1.0.0 (Current)
- ✅ Glassmorphism UI
- ✅ Multi-device input
- ✅ 10 action types
- ✅ Dynamic macros
- ✅ Configuration system
- ✅ Variable substitution

---

**Built with modern Python and PyQt6**
**Designed for power users and automation enthusiasts**

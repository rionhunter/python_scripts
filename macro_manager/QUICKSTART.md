# Quick Start Guide - Macro Manager

## Installation (5 minutes)

### Step 1: Install Python
If you don't have Python installed:
1. Download Python 3.8+ from https://www.python.org/
2. During installation, check "Add Python to PATH"
3. Verify: Open PowerShell and type `python --version`

### Step 2: Install Dependencies
```powershell
cd c:\Users\rionh\Documents\python_scripts\macro_manager
pip install -r requirements.txt
```

### Step 3: Launch
Double-click `launch.bat` or run:
```powershell
python macro_manager.py
```

## Creating Your First Macro (2 minutes)

### Example 1: Simple Text Paste
1. Click **"New Macro"** button
2. Enter name: "My First Macro"
3. Click **"Add Action"**
4. Select action type: **"Text Paste"**
5. Enter text: "Hello from Macro Manager!"
6. Click **OK**
7. Click **"Save Macro"**

### Example 2: Open Website
1. Click **"New Macro"**
2. Enter name: "Open GitHub"
3. Click **"Add Action"**
4. Select: **"Open URL"**
5. Enter URL: `https://github.com`
6. Click **OK**
7. Click **"Save Macro"**

### Example 3: Multi-Step Macro
1. Click **"New Macro"**
2. Enter name: "Quick Note"
3. Add these actions:
   - **Open Application**: `notepad.exe`
   - **Wait**: `1000` ms
   - **Text Paste**: "Meeting Notes - [Date]"
   - **Keyboard Press**: `enter`
4. Click **"Save Macro"**

## Executing Macros

### Method 1: Double-Click
- Double-click any macro in the list to edit/execute

### Method 2: Hotkey (Coming Soon)
- Assign hotkeys in settings
- Press hotkey to execute macro

### Method 3: Voice Command (Advanced)
1. Enable voice in settings
2. Speak: "execute [macro name]"

## Dynamic Macros (Advanced)

### Enable Dynamic Mode
1. Create/Edit a macro
2. Check ✓ **"Dynamic macro (accepts variables)"**
3. Add actions with variables like `{count}`, `{text}`

### Use Natural Language
Examples:
- "delete last 3 words" → Removes 3 words
- "wait 500 milliseconds" → Pauses 500ms
- "type 'Hello World'" → Types text

## Tips & Tricks

### ⌨️ Keyboard Shortcuts
- `Ctrl+N` - New macro
- `Ctrl+E` - Edit selected macro
- `Ctrl+D` - Delete selected macro
- `Ctrl+F` - Focus search box

### 🎯 Best Practices
1. **Name macros descriptively**: "Email Signature" not "Macro1"
2. **Group similar macros**: Use prefixes like "Email - ", "Code - "
3. **Add wait times**: Between actions that need time to complete
4. **Test step-by-step**: Build complex macros incrementally
5. **Backup macros**: Export config regularly

### 🔧 Common Actions

**Insert Clipboard:**
```
1. Keyboard Press: ctrl+v
```

**Select All:**
```
1. Keyboard Press: ctrl+a
```

**Copy Current Line:**
```
1. Keyboard Press: home
2. Keyboard Press: shift+end
3. Keyboard Press: ctrl+c
```

**Open File Explorer:**
```
1. Keyboard Press: win+e
```

**Switch to Browser:**
```
1. Switch Application: chrome (Name match)
```

## Troubleshooting

### "Module not found" error
```powershell
pip install [missing-module-name]
```

### Keyboard/Mouse not working
- **Windows**: Run as Administrator
- Check antivirus isn't blocking

### UI not appearing
- Check Python version: `python --version` (need 3.8+)
- Reinstall PyQt6: `pip install --force-reinstall PyQt6`

### Voice recognition not working
- Check microphone permissions
- Install: `pip install SpeechRecognition pyaudio`

## Next Steps

1. **Explore Examples**: Run `python demo.py` to see examples
2. **Customize UI**: Edit settings in `.macro_manager/settings.json`
3. **Add Input Devices**: Configure controllers, MIDI, etc.
4. **Create Templates**: Build your own macro library
5. **Share Macros**: Export and share with others

## Getting Help

- Check `README.md` for full documentation
- Review example macros in `demo.py`
- Check settings in `.macro_manager/` folder

---

**Ready to automate? Start creating macros now! 🚀**

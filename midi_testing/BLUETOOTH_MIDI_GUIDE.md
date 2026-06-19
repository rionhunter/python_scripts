# Bluetooth MIDI Solution Guide

## The Problem
Your **SMC-Mixer-bt** is a Bluetooth MIDI device that requires **BTMidiConnector.exe** to work. BTMidiConnector creates a virtual MIDI port called "SMC-Mixer-bt 0" but holds **exclusive access** to it, preventing other applications (like your Python scripts) from accessing it simultaneously.

## The Architecture
```
SMC-Mixer-bt (Bluetooth) → BTMidiConnector.exe → "SMC-Mixer-bt 0" port → ❌ Exclusive Access
```

## Solutions

### 🚀 **SOLUTION 1: Install loopMIDI (Recommended)**

1. **Download loopMIDI** (free): https://www.tobias-erichsen.de/software/loopmidi.html
2. **Install and run loopMIDI**
3. **Create a virtual port** called "SMC_Bridge"
4. **Configure BTMidiConnector** to output to "SMC_Bridge"
5. **Your Python scripts** read from "SMC_Bridge"

**New Architecture:**
```
SMC-Mixer-bt → BTMidiConnector → SMC_Bridge (virtual) → Your Python App ✅
```

### 🔧 **SOLUTION 2: Use MIDI-OX Router**

1. **Download MIDI-OX** (free): http://www.midiox.com/
2. **Set MIDI-OX input** to "SMC-Mixer-bt 0"
3. **Create virtual output port** in MIDI-OX
4. **Route MIDI** from SMC-Mixer-bt to virtual port
5. **Your Python scripts** read from virtual port

### ⚙️ **SOLUTION 3: Check BTMidiConnector Settings**

Some Bluetooth MIDI connectors support multiple outputs:
1. **Open BTMidiConnector settings**
2. **Look for "Output" or "Routing" options**
3. **Enable multiple clients** if available
4. **Add your Python application** as a client

### 🎯 **SOLUTION 4: Use Our Bridge Script**

Run the bridge script I created:
```bash
python bluetooth_midi_bridge.py
```

This script can create virtual ports and help with routing.

## Quick Test

Let's test your current setup:

1. **Keep BTMidiConnector running** (essential!)
2. **Run the bridge script**:
   ```bash
   python bluetooth_midi_bridge.py
   ```
3. **Try direct monitoring** (option 1) - it may work or fail
4. **If it fails**, use virtual port routing (option 2)

## Why This Happens

- **Bluetooth MIDI devices** need bridge software to connect to Windows
- **BTMidiConnector** is your bridge - it's essential
- **Windows MIDI API** uses exclusive access by design
- **Virtual MIDI routing** is the standard workaround

## Expected Workflow

1. **BTMidiConnector** connects to your SMC-Mixer-bt
2. **Virtual MIDI cable** (loopMIDI) creates shareable ports
3. **Route MIDI** from BTMidiConnector to virtual port
4. **Your Python apps** read from virtual port
5. **Multiple apps** can now access MIDI simultaneously

This is the standard setup for Bluetooth MIDI on Windows!
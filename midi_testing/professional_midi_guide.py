"""
SMC-Mixer-bt Direct Connection Guide
====================================

Since your BTMidiConnector is sketchy Alibaba software, let's try connecting
your SMC-Mixer-bt directly to Windows and route through loopMIDI.
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from utils import ColorPrinter

def show_connection_guide():
    """Show step-by-step guide for connecting SMC-Mixer-bt safely."""
    printer = ColorPrinter()
    printer.print_header("Safe SMC-Mixer-bt Connection Guide")
    
    print("STEP 1: Remove the sketchy BTMidiConnector")
    print("• Close BTMidiConnector.exe completely")
    print("• End all BTMidiConnector processes")
    print("• Consider uninstalling it entirely")
    print()
    
    print("STEP 2: Connect via Windows Bluetooth (Try This First)")
    print("• Open Settings → Bluetooth & devices")
    print("• Put SMC-Mixer-bt in pairing mode")
    print("• Click 'Add device' → Bluetooth")
    print("• Look for SMC-Mixer-bt in device list")
    print("• Connect as regular Bluetooth device")
    print()
    
    print("STEP 3: Check if Windows recognizes MIDI")
    print("• Run: python test_windows_native_midi.py")
    print("• See if Windows creates MIDI ports automatically")
    print("• Test for MIDI data from device")
    print()
    
    print("STEP 4: If Windows method fails, use Professional Software")
    print("• Download rtpMIDI: https://www.tobias-erichsen.de/software/rtpmidi.html")
    print("• This is professional, safe software (German developer)")
    print("• Used by musicians worldwide")
    print("• Supports Bluetooth MIDI properly")
    print()
    
    print("STEP 5: Route through loopMIDI (You already have this!)")
    print("• loopMIDI is already running (good!)")
    print("• Use loopMIDI Port 1 as your target")
    print("• Route SMC-Mixer → loopMIDI Port 1 → Your Python apps")
    print()
    
    print("🎯 GOAL: Replace sketchy Alibaba software with professional tools")
    print("✅ Windows native Bluetooth MIDI (preferred)")
    print("✅ rtpMIDI (professional alternative)")
    print("✅ loopMIDI for routing (you have this)")
    print("❌ Sketchy BTMidiConnector from Alibaba")

def test_current_setup():
    """Test current MIDI setup."""
    printer = ColorPrinter()
    printer.print_header("Current MIDI Setup Test")
    
    try:
        import rtmidi
        midi_in = rtmidi.MidiIn()
        
        printer.info("Available MIDI ports:")
        for i in range(midi_in.get_port_count()):
            port_name = midi_in.get_port_name(i)
            printer.print_colored(f"  {i}: {port_name}", 'cyan')
            
            # Try to test each port briefly
            try:
                test_midi = rtmidi.MidiIn()
                test_midi.open_port(i)
                printer.print_colored(f"    ✓ Port {i} accessible", 'green')
                test_midi.close_port()
                del test_midi
            except Exception as e:
                printer.print_colored(f"    ✗ Port {i} blocked: {str(e)[:50]}...", 'red')
        
        del midi_in
        
    except Exception as e:
        printer.error(f"Error testing MIDI setup: {e}")

def recommend_next_steps():
    """Recommend next steps based on current situation."""
    printer = ColorPrinter()
    printer.print_header("Recommended Next Steps")
    
    print("Based on your sketchy BTMidiConnector situation:")
    print()
    
    print("🚀 IMMEDIATE ACTION:")
    print("1. Download rtpMIDI (professional, safe): https://www.tobias-erichsen.de/software/rtpmidi.html")
    print("2. Uninstall BTMidiConnector completely")
    print("3. Connect SMC-Mixer-bt via rtpMIDI or Windows Bluetooth")
    print("4. Route MIDI through your existing loopMIDI setup")
    print()
    
    print("🎯 END GOAL:")
    print("SMC-Mixer-bt → Professional Software → loopMIDI Port 1 → Your Python Apps")
    print()
    
    print("✅ SAFE SOFTWARE SOURCES:")
    print("• rtpMIDI: https://www.tobias-erichsen.de/ (German, professional)")
    print("• loopMIDI: Same developer as above (you already have this)")
    print("• Windows native: Built into Windows 10/11")
    print()
    
    print("❌ AVOID:")
    print("• Sketchy Alibaba BTMidiConnector")
    print("• Random MIDI software from unknown sources")
    print("• Software without proper digital signatures")

def main():
    """Main menu."""
    print("SMC-Mixer-bt Professional Setup Guide")
    print("====================================")
    print()
    print("Your BTMidiConnector appears to be sketchy Alibaba software.")
    print("Let's replace it with professional, safe alternatives.")
    print()
    print("Options:")
    print("1. Show safe connection guide")
    print("2. Test current MIDI setup")
    print("3. Get professional software recommendations")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        show_connection_guide()
    elif choice == '2':
        test_current_setup()
    elif choice == '3':
        recommend_next_steps()
    elif choice == '4':
        print("Good luck with your professional MIDI setup! 🎵")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
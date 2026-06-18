"""
Quick test of loopMIDI Port access
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from utils import ColorPrinter
import time

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False

def test_loopmidi_access():
    printer = ColorPrinter()
    printer.print_header("Testing loopMIDI Port Access")
    
    if not RTMIDI_AVAILABLE:
        printer.error("rtmidi not available")
        return
    
    try:
        midi_in = rtmidi.MidiIn()
        
        # List ports
        printer.info("Available ports:")
        for i in range(midi_in.get_port_count()):
            port_name = midi_in.get_port_name(i)
            printer.print_colored(f"  {i}: {port_name}", 'cyan')
        
        # Try to open loopMIDI Port 1 (should be port 1)
        loopmidi_port = 1
        port_name = midi_in.get_port_name(loopmidi_port)
        
        if 'loopMIDI' not in port_name:
            printer.error("loopMIDI Port 1 not found at expected location")
            return
        
        printer.info(f"Attempting to open: {port_name}")
        
        midi_in.open_port(loopmidi_port)
        printer.success("Successfully opened loopMIDI Port 1!")
        
        def midi_callback(event, data=None):
            message, deltatime = event
            printer.print_colored(f"MIDI received: {list(message)}", 'bright_green')
        
        midi_in.set_callback(midi_callback)
        
        printer.info("Monitoring loopMIDI Port 1...")
        printer.info("Now set up MIDI routing from SMC-Mixer-bt 0 to loopMIDI Port 1")
        printer.info("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            midi_in.close_port()
            printer.info("Stopped monitoring")
            
    except Exception as e:
        printer.error(f"Error: {e}")

if __name__ == "__main__":
    test_loopmidi_access()
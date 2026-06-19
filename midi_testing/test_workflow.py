"""
Test your actual MIDI application workflow
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

def test_workflow():
    printer = ColorPrinter()
    printer.print_header("Test Your MIDI Workflow")
    
    if not RTMIDI_AVAILABLE:
        printer.error("rtmidi not available")
        return
    
    printer.info("This will test reading from loopMIDI Port 1")
    printer.info("If you can configure BTMidiConnector to send to loopMIDI Port 1,")
    printer.info("then your Python applications will work perfectly!")
    
    try:
        midi_in = rtmidi.MidiIn()
        
        # Open loopMIDI Port 1
        midi_in.open_port(1)  # loopMIDI Port 1
        printer.success("Successfully opened loopMIDI Port 1")
        
        message_count = 0
        
        def midi_callback(event, data=None):
            nonlocal message_count
            message, deltatime = event
            message_count += 1
            
            if len(message) >= 2:
                status = message[0]
                msg_type = status & 0xF0
                channel = (status & 0x0F) + 1
                
                if msg_type == 0x90 and len(message) >= 3:  # Note On
                    note = message[1]
                    velocity = message[2]
                    if velocity > 0:
                        printer.print_colored(
                            f"♪ Note On - Ch:{channel} Note:{note} Vel:{velocity}",
                            'bright_green'
                        )
                elif msg_type == 0xB0 and len(message) >= 3:  # Control Change
                    control = message[1]
                    value = message[2]
                    printer.print_colored(
                        f"🎛️ Control Change - Ch:{channel} CC:{control} Value:{value}",
                        'bright_cyan'
                    )
                else:
                    printer.print_colored(f"📡 MIDI: {list(message)}", 'white')
        
        midi_in.set_callback(midi_callback)
        
        printer.info("Listening for MIDI on loopMIDI Port 1...")
        printer.info("If BTMidiConnector routes to this port, you'll see MIDI data here")
        printer.info("Try moving controls on your SMC-Mixer-bt...")
        printer.info("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            midi_in.close_port()
            if message_count > 0:
                printer.success(f"SUCCESS! Received {message_count} MIDI messages")
                printer.success("Your Python MIDI applications will work with loopMIDI Port 1!")
            else:
                printer.warning("No MIDI messages received")
                printer.info("You need to configure BTMidiConnector to route to loopMIDI Port 1")
                
    except Exception as e:
        printer.error(f"Error: {e}")

if __name__ == "__main__":
    test_workflow()
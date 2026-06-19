"""
Test Brooklyn MIDI Bridge
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from utils import ColorPrinter
import time

try:
    import rtmidi
except ImportError:
    print("rtmidi not available")
    sys.exit(1)

def test_brooklyn_port():
    """Test the Brooklyn 1 MIDI port."""
    printer = ColorPrinter()
    printer.print_header("Testing Brooklyn 1 MIDI Port")
    
    try:
        midi_in = rtmidi.MidiIn()
        
        # List all ports
        printer.info("Available MIDI ports:")
        for i in range(midi_in.get_port_count()):
            port_name = midi_in.get_port_name(i)
            printer.print_colored(f"  {i}: {port_name}", 'cyan')
        
        # Try to open Brooklyn 1 (should be port 1)
        brooklyn_port = 1
        port_name = midi_in.get_port_name(brooklyn_port)
        
        if 'Brooklyn' not in port_name:
            printer.error("Brooklyn 1 not found at expected port")
            return
        
        printer.info(f"Opening: {port_name}")
        midi_in.open_port(brooklyn_port)
        printer.success("Successfully opened Brooklyn 1!")
        
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
                            f"🎹 Note On - Ch:{channel} Note:{note} Vel:{velocity}",
                            'bright_green'
                        )
                    else:
                        printer.print_colored(
                            f"🎹 Note Off - Ch:{channel} Note:{note}",
                            'yellow'
                        )
                elif msg_type == 0x80 and len(message) >= 3:  # Note Off
                    note = message[1]
                    printer.print_colored(
                        f"🎹 Note Off - Ch:{channel} Note:{note}",
                        'yellow'
                    )
                elif msg_type == 0xB0 and len(message) >= 3:  # Control Change
                    control = message[1]
                    value = message[2]
                    printer.print_colored(
                        f"🎛️ Control Change - Ch:{channel} CC:{control} Value:{value}",
                        'bright_cyan'
                    )
                elif msg_type == 0xE0 and len(message) >= 3:  # Pitch Bend
                    lsb = message[1]
                    msb = message[2]
                    value = (msb << 7) | lsb
                    printer.print_colored(
                        f"🎵 Pitch Bend - Ch:{channel} Value:{value}",
                        'magenta'
                    )
                else:
                    printer.print_colored(f"📡 MIDI: {list(message)}", 'white')
        
        midi_in.set_callback(midi_callback)
        
        printer.success("Monitoring Brooklyn 1 for MIDI data...")
        printer.info("Try using your SMC-Mixer-bt controls!")
        printer.info("• Move faders/knobs")
        printer.info("• Press buttons")
        printer.info("• Try any controls on the device")
        printer.info("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            midi_in.close_port()
            
            if message_count > 0:
                printer.success(f"🎉 SUCCESS! Received {message_count} MIDI messages!")
                printer.success("Your MIDI bridge is working!")
                printer.print_header("Great News!")
                print("✅ Brooklyn 1 is receiving MIDI from your SMC-Mixer-bt")
                print("✅ Your Python applications can now use Brooklyn 1 instead of SMC-Mixer-bt 0")
                print("✅ Use device string: 'rtmidi:1:Brooklyn 1'")
                print("✅ No more exclusive access issues!")
            else:
                printer.warning("No MIDI messages received")
                printer.info("Try:")
                printer.info("• Make sure your SMC-Mixer-bt is connected")
                printer.info("• Move controls on the device")
                printer.info("• Check if your bridge software is properly routing")
                
    except Exception as e:
        printer.error(f"Error: {e}")

if __name__ == "__main__":
    test_brooklyn_port()
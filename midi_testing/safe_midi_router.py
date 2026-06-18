"""
Safe MIDI Router - Alternative to MIDI-OX using only trusted software
"""

import sys
import time
import threading
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from utils import ColorPrinter

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False

class SafeMIDIRouter:
    """Safe MIDI routing without requiring external downloads."""
    
    def __init__(self):
        self.printer = ColorPrinter()
        self.routing = False
        self.message_count = 0
    
    def create_python_midi_bridge(self):
        """Create a Python-based MIDI bridge from SMC-Mixer to loopMIDI."""
        if not RTMIDI_AVAILABLE:
            self.printer.error("rtmidi not available")
            return False
        
        self.printer.print_header("Python MIDI Bridge")
        self.printer.info("This will route MIDI from SMC-Mixer-bt 0 to loopMIDI Port 1")
        
        try:
            # Try to open input from SMC-Mixer (may fail due to exclusive access)
            midi_in = rtmidi.MidiIn()
            midi_out = rtmidi.MidiOut()
            
            # List available ports
            self.printer.info("Available input ports:")
            for i in range(midi_in.get_port_count()):
                port_name = midi_in.get_port_name(i)
                self.printer.print_colored(f"  {i}: {port_name}", 'cyan')
            
            self.printer.info("Available output ports:")
            for i in range(midi_out.get_port_count()):
                port_name = midi_out.get_port_name(i)
                self.printer.print_colored(f"  {i}: {port_name}", 'cyan')
            
            # Try to open SMC-Mixer input (port 0)
            try:
                self.printer.info("Attempting to open SMC-Mixer-bt 0 for input...")
                midi_in.open_port(0)  # SMC-Mixer-bt 0
                self.printer.success("Successfully opened SMC-Mixer-bt 0!")
                
                # Open loopMIDI output (port 1)
                self.printer.info("Opening loopMIDI Port 1 for output...")
                midi_out.open_port(1)  # loopMIDI Port 1
                self.printer.success("Successfully opened loopMIDI Port 1!")
                
                # Set up routing callback
                def route_midi(event, data=None):
                    message, deltatime = event
                    self.message_count += 1
                    # Forward the message to loopMIDI
                    midi_out.send_message(message)
                    self.printer.print_colored(f"Routed: {list(message)}", 'bright_green')
                
                midi_in.set_callback(route_midi)
                
                self.printer.success("MIDI routing active!")
                self.printer.info("MIDI from SMC-Mixer-bt is now being routed to loopMIDI Port 1")
                self.printer.info("Your other applications can now read from loopMIDI Port 1")
                self.printer.info("Press Ctrl+C to stop routing")
                
                self.routing = True
                try:
                    while self.routing:
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    pass
                finally:
                    self.routing = False
                    midi_in.close_port()
                    midi_out.close_port()
                    self.printer.info(f"Routing stopped. Forwarded {self.message_count} messages.")
                    return True
                    
            except Exception as e:
                self.printer.error(f"Cannot open SMC-Mixer-bt 0: {e}")
                self.printer.info("This is expected due to BTMidiConnector's exclusive access")
                return False
                
        except Exception as e:
            self.printer.error(f"Error setting up MIDI bridge: {e}")
            return False
    
    def test_alternative_backends(self):
        """Test if alternative backends can access the SMC device."""
        self.printer.print_header("Testing Alternative MIDI Backends")
        
        # Test with mido
        try:
            import mido
            self.printer.info("Testing with mido backend...")
            
            input_names = mido.get_input_names()
            output_names = mido.get_output_names()
            
            self.printer.info("Mido input ports:")
            for name in input_names:
                self.printer.print_colored(f"  {name}", 'cyan')
            
            # Try to open SMC-Mixer with mido
            smc_port = None
            loopmidi_port = None
            
            for name in input_names:
                if 'SMC-Mixer-bt' in name:
                    smc_port = name
                    break
            
            for name in output_names:
                if 'loopMIDI' in name:
                    loopmidi_port = name
                    break
            
            if smc_port and loopmidi_port:
                try:
                    self.printer.info(f"Attempting mido bridge: {smc_port} → {loopmidi_port}")
                    
                    with mido.open_input(smc_port) as inport, mido.open_output(loopmidi_port) as outport:
                        self.printer.success("Mido bridge established!")
                        self.printer.info("Routing MIDI messages... Press Ctrl+C to stop")
                        
                        try:
                            for message in inport:
                                outport.send(message)
                                self.message_count += 1
                                self.printer.print_colored(f"Routed: {message}", 'bright_green')
                        except KeyboardInterrupt:
                            pass
                        finally:
                            self.printer.info(f"Mido routing stopped. Forwarded {self.message_count} messages.")
                            return True
                            
                except Exception as e:
                    self.printer.error(f"Mido bridge failed: {e}")
                    
        except ImportError:
            self.printer.warning("mido not available")
        except Exception as e:
            self.printer.error(f"Mido test failed: {e}")
        
        return False
    
    def provide_safe_alternatives(self):
        """Provide information about safe MIDI routing alternatives."""
        self.printer.print_header("Safe MIDI Routing Alternatives")
        
        print("Since MIDI-OX appears to have security issues, here are safer options:")
        print()
        
        print("✅ OPTION 1: Reaper (Professional DAW with free trial)")
        print("   • Download: https://www.reaper.fm/download.php")
        print("   • Has built-in MIDI routing")
        print("   • Very reputable software company")
        print("   • Can route MIDI between devices")
        print()
        
        print("✅ OPTION 2: VoiceMeeter (Free audio/MIDI router)")
        print("   • Download: https://vb-audio.com/Voicemeeter/")
        print("   • Well-known, trusted software")
        print("   • Includes MIDI routing capabilities")
        print()
        
        print("✅ OPTION 3: ASIO4ALL + DAW")
        print("   • Download ASIO4ALL: https://www.asio4all.org/")
        print("   • Use with any free DAW (Audacity, etc.)")
        print("   • ASIO4ALL is industry standard")
        print()
        
        print("✅ OPTION 4: Our Python Bridge (No downloads needed)")
        print("   • Use the Python MIDI bridge I just created")
        print("   • No external downloads required")
        print("   • May work if BTMidiConnector allows multiple connections")
        print()
        
        print("✅ OPTION 5: BTMidiConnector Settings")
        print("   • Check BTMidiConnector for routing options")
        print("   • Some BT MIDI connectors support multiple outputs")
        print("   • Look for 'Share' or 'Multi-client' options")
        print()
        
        print("🔒 All these options are from reputable sources and much safer!")

def main():
    router = SafeMIDIRouter()
    
    print("Safe MIDI Routing Options:")
    print("1. Try Python-based MIDI bridge (may work)")
    print("2. Test alternative MIDI backends")
    print("3. Show safe software alternatives")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        success = router.create_python_midi_bridge()
        if not success:
            print("\nPython bridge failed due to exclusive access.")
            print("Try option 3 for safe external software alternatives.")
    
    elif choice == '2':
        success = router.test_alternative_backends()
        if not success:
            print("\nAlternative backends also failed.")
            print("This confirms exclusive access issue. Try option 3.")
    
    elif choice == '3':
        router.provide_safe_alternatives()
    
    elif choice == '4':
        print("Goodbye!")
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
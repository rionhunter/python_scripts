"""
Bluetooth MIDI Bridge Solution
==============================

This script works alongside BTMidiConnector.exe to access your Bluetooth MIDI device.
Instead of trying to compete for exclusive access, we'll set up MIDI routing.
"""

import sys
import time
import subprocess
from pathlib import Path

# Add the midi_testing directory to the path
sys.path.append(str(Path(__file__).parent))

from utils import ColorPrinter

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False

try:
    import mido
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False

class BluetoothMIDIBridge:
    """Bridge solution for Bluetooth MIDI devices using BTMidiConnector."""
    
    def __init__(self):
        self.printer = ColorPrinter()
        self.virtual_port = None
        self.monitoring = False
        self.message_count = 0
    
    def check_btmidiconnector_status(self):
        """Check if BTMidiConnector is running and configured properly."""
        self.printer.print_header("Bluetooth MIDI Bridge Status")
        
        # Check if BTMidiConnector is running
        import psutil
        btmidi_running = False
        btmidi_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'BTMidiConnector' in proc.info['name']:
                    btmidi_running = True
                    btmidi_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if btmidi_running:
            self.printer.success(f"BTMidiConnector is running ({len(btmidi_processes)} process(es))")
            for proc in btmidi_processes:
                self.printer.print_colored(f"  PID {proc['pid']}: {proc['name']}", 'cyan')
        else:
            self.printer.error("BTMidiConnector is not running!")
            self.printer.info("Please start BTMidiConnector to enable Bluetooth MIDI")
            return False
        
        return True
    
    def list_available_ports(self):
        """List all available MIDI ports including virtual ones."""
        self.printer.info("Scanning for available MIDI ports...")
        
        if RTMIDI_AVAILABLE:
            try:
                midi_in = rtmidi.MidiIn()
                input_ports = []
                for i in range(midi_in.get_port_count()):
                    port_name = midi_in.get_port_name(i)
                    input_ports.append((i, port_name))
                
                if input_ports:
                    self.printer.success("Available MIDI input ports:")
                    for i, name in input_ports:
                        self.printer.print_colored(f"  {i}: {name}", 'cyan')
                else:
                    self.printer.warning("No MIDI input ports found")
                
                del midi_in
                return input_ports
                
            except Exception as e:
                self.printer.error(f"Error listing ports: {e}")
        
        return []
    
    def create_virtual_port_bridge(self):
        """Create a virtual MIDI port that can receive from BTMidiConnector."""
        if not RTMIDI_AVAILABLE:
            self.printer.error("python-rtmidi not available for virtual port creation")
            return False
        
        try:
            self.printer.info("Creating virtual MIDI bridge port...")
            
            # Create a virtual input port that other applications can send to
            self.virtual_port = rtmidi.MidiIn()
            self.virtual_port.open_virtual_port("BT_MIDI_Bridge_Input")
            
            self.printer.success("Virtual bridge port created: 'BT_MIDI_Bridge_Input'")
            self.printer.info("Now you can route BTMidiConnector output to this virtual port")
            
            return True
            
        except Exception as e:
            self.printer.error(f"Failed to create virtual port: {e}")
            return False
    
    def monitor_virtual_port(self):
        """Monitor the virtual port for incoming MIDI messages."""
        if not self.virtual_port:
            self.printer.error("No virtual port created!")
            return
        
        self.printer.success("Monitoring virtual bridge port...")
        self.printer.info("Configure BTMidiConnector to send to 'BT_MIDI_Bridge_Input'")
        self.printer.info("Press Ctrl+C to stop monitoring")
        
        self.virtual_port.set_callback(self._midi_callback)
        self.monitoring = True
        self.message_count = 0
        
        try:
            while self.monitoring:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.monitoring = False
            self.printer.info(f"Stopped monitoring. Received {self.message_count} messages.")
    
    def _midi_callback(self, event, data=None):
        """Handle incoming MIDI messages."""
        message, deltatime = event
        self.message_count += 1
        
        if len(message) >= 2:
            status = message[0]
            msg_type = status & 0xF0
            channel = (status & 0x0F) + 1
            
            if msg_type == 0x90 and len(message) >= 3:  # Note On
                note = message[1]
                velocity = message[2]
                if velocity > 0:
                    note_name = self._note_to_name(note)
                    self.printer.print_colored(
                        f"♪ Note On - Ch:{channel} Note:{note} ({note_name}) Vel:{velocity}",
                        'bright_green'
                    )
                else:
                    note_name = self._note_to_name(note)
                    self.printer.print_colored(
                        f"♪ Note Off - Ch:{channel} Note:{note} ({note_name})",
                        'yellow'
                    )
            elif msg_type == 0x80 and len(message) >= 3:  # Note Off
                note = message[1]
                note_name = self._note_to_name(note)
                self.printer.print_colored(
                    f"♪ Note Off - Ch:{channel} Note:{note} ({note_name})",
                    'yellow'
                )
            elif msg_type == 0xB0 and len(message) >= 3:  # Control Change
                control = message[1]
                value = message[2]
                self.printer.print_colored(
                    f"► CC - Ch:{channel} Control:{control} Value:{value}",
                    'cyan'
                )
            else:
                self.printer.print_colored(f"► Raw MIDI: {list(message)}", 'white')
    
    def _note_to_name(self, note_number):
        """Convert MIDI note number to note name."""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (note_number // 12) - 1
        note = notes[note_number % 12]
        return f"{note}{octave}"
    
    def try_direct_monitoring(self):
        """Try to monitor BTMidiConnector's port directly (may fail due to exclusive access)."""
        self.printer.info("Attempting direct monitoring of BTMidiConnector port...")
        
        ports = self.list_available_ports()
        smc_port = None
        
        for port_id, port_name in ports:
            if 'SMC-Mixer-bt' in port_name:
                smc_port = (port_id, port_name)
                break
        
        if not smc_port:
            self.printer.error("SMC-Mixer-bt port not found!")
            return False
        
        port_id, port_name = smc_port
        self.printer.info(f"Found SMC-Mixer-bt at port {port_id}: {port_name}")
        
        try:
            midi_in = rtmidi.MidiIn()
            midi_in.open_port(port_id)
            midi_in.set_callback(self._midi_callback)
            
            self.printer.success("Direct monitoring started!")
            self.printer.info("Play something on your SMC-Mixer-bt... Press Ctrl+C to stop")
            
            self.monitoring = True
            self.message_count = 0
            
            try:
                while self.monitoring:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
            finally:
                self.monitoring = False
                midi_in.close_port()
                self.printer.info(f"Stopped monitoring. Received {self.message_count} messages.")
                del midi_in
                return True
                
        except Exception as e:
            self.printer.error(f"Direct monitoring failed: {e}")
            self.printer.info("This is expected due to exclusive access. Use the virtual port method instead.")
            return False
    
    def provide_routing_instructions(self):
        """Provide instructions for routing BTMidiConnector through virtual ports."""
        self.printer.print_header("MIDI Routing Setup Instructions")
        
        print("Since BTMidiConnector has exclusive access to your SMC-Mixer-bt,")
        print("you need to set up MIDI routing. Here are your options:")
        print()
        
        print("OPTION 1: Use Virtual MIDI Cable Software")
        print("1. Download and install 'loopMIDI' (free virtual MIDI cable)")
        print("2. Create a virtual MIDI port called 'SMC_Bridge'")
        print("3. Configure BTMidiConnector to send MIDI to 'SMC_Bridge'")
        print("4. Your Python applications can then read from 'SMC_Bridge'")
        print()
        
        print("OPTION 2: Use MIDI-OX for Routing")
        print("1. Download and install MIDI-OX (free MIDI router)")
        print("2. Set input from 'SMC-Mixer-bt 0'")
        print("3. Set output to a virtual port")
        print("4. Your Python applications read from the virtual port")
        print()
        
        print("OPTION 3: Check BTMidiConnector Settings")
        print("1. Look for routing or output options in BTMidiConnector")
        print("2. See if it can output to multiple destinations")
        print("3. Some Bluetooth MIDI connectors support multiple clients")
        print()
        
        print("DOWNLOAD LINKS:")
        print("• loopMIDI: https://www.tobias-erichsen.de/software/loopmidi.html")
        print("• MIDI-OX: http://www.midiox.com/")

def main():
    """Main function for the Bluetooth MIDI bridge."""
    bridge = BluetoothMIDIBridge()
    
    # Check BTMidiConnector status
    if not bridge.check_btmidiconnector_status():
        print("\nPlease start BTMidiConnector and try again.")
        return
    
    # List available ports
    ports = bridge.list_available_ports()
    
    print("\nWhat would you like to do?")
    print("1. Try direct monitoring (may fail due to exclusive access)")
    print("2. Create virtual bridge port for routing")
    print("3. Show MIDI routing setup instructions")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == '1':
        success = bridge.try_direct_monitoring()
        if not success:
            print("\nDirect monitoring failed. Try option 2 or 3 for routing solutions.")
    
    elif choice == '2':
        if bridge.create_virtual_port_bridge():
            print("\nVirtual port created! Now configure BTMidiConnector to use it.")
            response = input("Monitor the virtual port for incoming messages? (y/n): ")
            if response.lower() == 'y':
                bridge.monitor_virtual_port()
    
    elif choice == '3':
        bridge.provide_routing_instructions()
    
    elif choice == '4':
        print("Goodbye!")
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
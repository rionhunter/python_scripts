"""
MIDI Input Tester - Tests MIDI input functionality and monitors incoming messages.
"""

import time
import threading
from utils import ColorPrinter, format_midi_message, note_number_to_name, velocity_to_bar

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

try:
    import pygame
    import pygame.midi
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class MIDIInputTester:
    """Tests MIDI input functionality."""
    
    def __init__(self):
        self.printer = ColorPrinter()
        self.monitoring = False
        self.message_count = 0
        self.note_states = {}  # Track which notes are currently on
    
    def test_device(self, device_string):
        """Test a specific MIDI input device."""
        backend, device_id, device_name = self._parse_device_string(device_string)
        
        if backend is None:
            self.printer.error("Invalid device string format")
            return
        
        self.printer.info(f"Testing device: {device_name} (backend: {backend})")
        
        if backend == 'rtmidi':
            self._test_rtmidi_input(device_id)
        elif backend == 'mido':
            self._test_mido_input(device_name)
        elif backend == 'pygame':
            self._test_pygame_input(device_id)
        else:
            self.printer.error(f"Unsupported backend: {backend}")
    
    def _parse_device_string(self, device_string):
        """Parse device string to extract backend and device info."""
        try:
            parts = device_string.split(':', 2)
            backend = parts[0]
            
            if backend == 'rtmidi':
                device_id = int(parts[1])
                device_name = parts[2] if len(parts) > 2 else f"Device {device_id}"
                return backend, device_id, device_name
            elif backend == 'mido':
                device_name = ':'.join(parts[1:])
                return backend, None, device_name
            elif backend == 'pygame':
                device_id = int(parts[1])
                device_name = parts[2] if len(parts) > 2 else f"Device {device_id}"
                return backend, device_id, device_name
            
        except Exception as e:
            self.printer.error(f"Error parsing device string: {e}")
        
        return None, None, device_string
    
    def _test_rtmidi_input(self, device_id):
        """Test MIDI input using python-rtmidi."""
        if not RTMIDI_AVAILABLE:
            self.printer.error("python-rtmidi not available")
            return
        
        try:
            midi_in = rtmidi.MidiIn()
            
            if device_id >= midi_in.get_port_count():
                self.printer.error(f"Device ID {device_id} not found")
                return
            
            midi_in.open_port(device_id)
            midi_in.set_callback(self._rtmidi_callback)
            
            self.printer.success("MIDI input opened successfully")
            self.printer.info("Listening for MIDI messages... (Press Ctrl+C to stop)")
            
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
                
        except Exception as e:
            self.printer.error(f"Error testing rtmidi input: {e}")
    
    def _test_mido_input(self, device_name):
        """Test MIDI input using mido."""
        if not MIDO_AVAILABLE:
            self.printer.error("mido not available")
            return
        
        try:
            with mido.open_input(device_name) as inport:
                self.printer.success("MIDI input opened successfully")
                self.printer.info("Listening for MIDI messages... (Press Ctrl+C to stop)")
                
                self.monitoring = True
                self.message_count = 0
                
                try:
                    for message in inport:
                        if not self.monitoring:
                            break
                        self._process_mido_message(message)
                except KeyboardInterrupt:
                    pass
                finally:
                    self.monitoring = False
                    self.printer.info(f"Stopped monitoring. Received {self.message_count} messages.")
                    
        except Exception as e:
            self.printer.error(f"Error testing mido input: {e}")
    
    def _test_pygame_input(self, device_id):
        """Test MIDI input using pygame."""
        if not PYGAME_AVAILABLE:
            self.printer.error("pygame not available")
            return
        
        try:
            pygame.midi.init()
            
            if device_id >= pygame.midi.get_count():
                self.printer.error(f"Device ID {device_id} not found")
                return
            
            midi_input = pygame.midi.Input(device_id)
            
            self.printer.success("MIDI input opened successfully")
            self.printer.info("Listening for MIDI messages... (Press Ctrl+C to stop)")
            
            self.monitoring = True
            self.message_count = 0
            
            try:
                while self.monitoring:
                    if midi_input.poll():
                        midi_events = midi_input.read(10)
                        for event in midi_events:
                            self._process_pygame_message(event)
                    time.sleep(0.01)
            except KeyboardInterrupt:
                pass
            finally:
                self.monitoring = False
                midi_input.close()
                pygame.midi.quit()
                self.printer.info(f"Stopped monitoring. Received {self.message_count} messages.")
                
        except Exception as e:
            self.printer.error(f"Error testing pygame input: {e}")
    
    def _rtmidi_callback(self, event, data=None):
        """Callback for rtmidi messages."""
        message, deltatime = event
        self._process_raw_midi_message(message)
    
    def _process_mido_message(self, message):
        """Process a mido MIDI message."""
        self.message_count += 1
        formatted = format_midi_message(message)
        
        # Add extra details for certain message types
        if message.type == 'note_on' and message.velocity > 0:
            note_name = note_number_to_name(message.note)
            velocity_bar = velocity_to_bar(message.velocity)
            self.note_states[message.note] = True
            self.printer.print_colored(
                f"♪ {formatted} ({note_name}) {velocity_bar}",
                'bright_green'
            )
        elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
            note_name = note_number_to_name(message.note)
            self.note_states.pop(message.note, None)
            self.printer.print_colored(
                f"♪ {formatted} ({note_name})",
                'green'
            )
        elif message.type == 'control_change':
            self.printer.print_colored(formatted, 'yellow')
        elif message.type == 'program_change':
            self.printer.print_colored(formatted, 'magenta')
        elif message.type == 'pitchwheel':
            self.printer.print_colored(formatted, 'cyan')
        else:
            self.printer.print_colored(formatted, 'white')
        
        # Show active notes count
        if self.note_states:
            active_notes = len(self.note_states)
            self.printer.print_colored(f"    Active notes: {active_notes}", 'blue')
    
    def _process_pygame_message(self, event):
        """Process a pygame MIDI message."""
        midi_data, timestamp = event
        self._process_raw_midi_message(midi_data)
    
    def _process_raw_midi_message(self, midi_data):
        """Process raw MIDI data."""
        self.message_count += 1
        
        if len(midi_data) >= 3:
            status, data1, data2 = midi_data[0], midi_data[1], midi_data[2]
            
            # Parse MIDI message
            message_type = status & 0xF0
            channel = status & 0x0F
            
            if message_type == 0x90 and data2 > 0:  # Note On
                note_name = note_number_to_name(data1)
                velocity_bar = velocity_to_bar(data2)
                self.note_states[data1] = True
                self.printer.print_colored(
                    f"♪ Note On - Ch:{channel} Note:{data1} ({note_name}) Vel:{data2} {velocity_bar}",
                    'bright_green'
                )
            elif message_type == 0x80 or (message_type == 0x90 and data2 == 0):  # Note Off
                note_name = note_number_to_name(data1)
                self.note_states.pop(data1, None)
                self.printer.print_colored(
                    f"♪ Note Off - Ch:{channel} Note:{data1} ({note_name}) Vel:{data2}",
                    'green'
                )
            elif message_type == 0xB0:  # Control Change
                self.printer.print_colored(
                    f"CC - Ch:{channel} Control:{data1} Value:{data2}",
                    'yellow'
                )
            elif message_type == 0xC0:  # Program Change
                self.printer.print_colored(
                    f"Program Change - Ch:{channel} Program:{data1}",
                    'magenta'
                )
            elif message_type == 0xE0:  # Pitch Bend
                pitch_value = (data2 << 7) | data1
                self.printer.print_colored(
                    f"Pitch Bend - Ch:{channel} Value:{pitch_value}",
                    'cyan'
                )
            else:
                self.printer.print_colored(
                    f"MIDI: {hex(status)} {data1} {data2}",
                    'white'
                )
            
            # Show active notes count
            if self.note_states:
                active_notes = len(self.note_states)
                self.printer.print_colored(f"    Active notes: {active_notes}", 'blue')
        else:
            self.printer.print_colored(f"Raw MIDI: {midi_data}", 'white')
    
    def real_time_monitor(self):
        """Run a real-time MIDI monitor for all available input devices."""
        from device_scanner import MIDIDeviceScanner
        
        scanner = MIDIDeviceScanner()
        input_devices = scanner.get_input_devices()
        
        if not input_devices:
            self.printer.error("No MIDI input devices found!")
            return
        
        print("Available input devices:")
        for i, device in enumerate(input_devices):
            print(f"{i}: {device}")
        
        try:
            choice = int(input(f"\nSelect device to monitor (0-{len(input_devices)-1}): "))
            if 0 <= choice < len(input_devices):
                print("\nStarting real-time monitor...")
                print("Message format: Type - Channel:Note/Control Value [Extra Info]")
                print("Press Ctrl+C to stop\n")
                self.test_device(input_devices[choice])
            else:
                self.printer.error("Invalid device selection.")
        except ValueError:
            self.printer.error("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            self.printer.info("Monitor stopped by user.")

if __name__ == "__main__":
    tester = MIDIInputTester()
    tester.real_time_monitor()
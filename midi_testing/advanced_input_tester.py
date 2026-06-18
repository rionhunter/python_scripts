"""
Advanced MIDI Input Tester - Enhanced testing with better error handling and Windows compatibility.
"""

import time
import threading
import sys
import os
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

class AdvancedMIDIInputTester:
    """Enhanced MIDI input tester with better Windows compatibility."""
    
    def __init__(self):
        self.printer = ColorPrinter()
        self.monitoring = False
        self.message_count = 0
        self.note_states = {}
        self.successful_backends = []
        self.failed_backends = {}
    
    def test_device_all_backends(self, device_string):
        """Test a device with all available backends to find which ones work."""
        backend, device_id, device_name = self._parse_device_string(device_string)
        
        if backend is None:
            self.printer.error("Invalid device string format")
            return False
        
        self.printer.print_header(f"Comprehensive Testing: {device_name}")
        self.printer.info(f"Original backend: {backend}")
        
        success = False
        
        # Test with all available backends
        if RTMIDI_AVAILABLE:
            if self._test_rtmidi_compatibility(device_name):
                success = True
        
        if MIDO_AVAILABLE:
            if self._test_mido_compatibility(device_name):
                success = True
        
        if PYGAME_AVAILABLE:
            if self._test_pygame_compatibility(device_name):
                success = True
        
        # Summary
        self._print_compatibility_summary()
        
        return success
    
    def _test_rtmidi_compatibility(self, target_device_name):
        """Test rtmidi compatibility with enhanced error handling."""
        self.printer.info("Testing python-rtmidi backend...")
        
        if not RTMIDI_AVAILABLE:
            self.failed_backends['rtmidi'] = "Library not available"
            return False
        
        try:
            midi_in = rtmidi.MidiIn()
            
            # Find device by name
            device_id = None
            for i in range(midi_in.get_port_count()):
                port_name = midi_in.get_port_name(i)
                if target_device_name in port_name or port_name in target_device_name:
                    device_id = i
                    break
            
            if device_id is None:
                self.failed_backends['rtmidi'] = f"Device '{target_device_name}' not found"
                return False
            
            # Try different approaches to open the port
            success = False
            error_messages = []
            
            # Approach 1: Standard open
            try:
                midi_in.open_port(device_id)
                self.printer.success("✓ rtmidi: Standard port opening successful")
                success = True
                midi_in.close_port()
            except Exception as e:
                error_messages.append(f"Standard open: {str(e)}")
            
            # Approach 2: Try with different client name
            if not success:
                try:
                    midi_in2 = rtmidi.MidiIn(name="MIDI_Test_Client")
                    midi_in2.open_port(device_id)
                    self.printer.success("✓ rtmidi: Custom client name successful")
                    success = True
                    midi_in2.close_port()
                    del midi_in2
                except Exception as e:
                    error_messages.append(f"Custom client: {str(e)}")
            
            # Approach 3: Virtual port test
            if not success:
                try:
                    midi_in3 = rtmidi.MidiIn()
                    midi_in3.open_virtual_port("Test_Virtual_Port")
                    self.printer.warning("✓ rtmidi: Virtual port creation works (device port failed)")
                    midi_in3.close_port()
                    del midi_in3
                except Exception as e:
                    error_messages.append(f"Virtual port: {str(e)}")
            
            del midi_in
            
            if success:
                self.successful_backends.append('rtmidi')
                return True
            else:
                self.failed_backends['rtmidi'] = "; ".join(error_messages)
                return False
                
        except Exception as e:
            self.failed_backends['rtmidi'] = f"Backend initialization failed: {str(e)}"
            return False
    
    def _test_mido_compatibility(self, target_device_name):
        """Test mido compatibility."""
        self.printer.info("Testing mido backend...")
        
        if not MIDO_AVAILABLE:
            self.failed_backends['mido'] = "Library not available"
            return False
        
        try:
            # Find device by name
            available_inputs = mido.get_input_names()
            matching_device = None
            
            for device in available_inputs:
                if target_device_name in device or device in target_device_name:
                    matching_device = device
                    break
            
            if matching_device is None:
                self.failed_backends['mido'] = f"Device '{target_device_name}' not found in {available_inputs}"
                return False
            
            # Test opening the device
            try:
                with mido.open_input(matching_device) as inport:
                    self.printer.success("✓ mido: Device opened successfully")
                    self.successful_backends.append('mido')
                    return True
            except Exception as e:
                self.failed_backends['mido'] = f"Port open failed: {str(e)}"
                return False
                
        except Exception as e:
            self.failed_backends['mido'] = f"Backend error: {str(e)}"
            return False
    
    def _test_pygame_compatibility(self, target_device_name):
        """Test pygame compatibility."""
        self.printer.info("Testing pygame backend...")
        
        if not PYGAME_AVAILABLE:
            self.failed_backends['pygame'] = "Library not available"
            return False
        
        try:
            pygame.midi.init()
            
            # Find device by name
            device_id = None
            for i in range(pygame.midi.get_count()):
                info = pygame.midi.get_device_info(i)
                name = info[1].decode('utf-8')
                is_input = info[2]
                
                if is_input and (target_device_name in name or name in target_device_name):
                    device_id = i
                    break
            
            if device_id is None:
                pygame.midi.quit()
                self.failed_backends['pygame'] = f"Device '{target_device_name}' not found"
                return False
            
            # Test opening the device
            try:
                midi_input = pygame.midi.Input(device_id)
                self.printer.success("✓ pygame: Device opened successfully")
                midi_input.close()
                pygame.midi.quit()
                self.successful_backends.append('pygame')
                return True
            except Exception as e:
                pygame.midi.quit()
                self.failed_backends['pygame'] = f"Port open failed: {str(e)}"
                return False
                
        except Exception as e:
            try:
                pygame.midi.quit()
            except:
                pass
            self.failed_backends['pygame'] = f"Backend error: {str(e)}"
            return False
    
    def _print_compatibility_summary(self):
        """Print a summary of backend compatibility."""
        self.printer.print_header("Backend Compatibility Summary")
        
        if self.successful_backends:
            self.printer.success("Working backends:")
            for backend in self.successful_backends:
                self.printer.print_colored(f"  ✓ {backend}", 'bright_green')
        else:
            self.printer.error("No backends successfully opened the device!")
        
        if self.failed_backends:
            self.printer.warning("Failed backends:")
            for backend, error in self.failed_backends.items():
                self.printer.print_colored(f"  ✗ {backend}: {error}", 'red')
    
    def test_with_working_backend(self, device_string):
        """Test device using the first working backend found."""
        if not self.successful_backends:
            self.printer.error("No working backends found. Run comprehensive test first.")
            return
        
        backend = self.successful_backends[0]
        self.printer.info(f"Using working backend: {backend}")
        
        backend_obj, device_id, device_name = self._parse_device_string(device_string)
        
        if backend == 'rtmidi':
            self._monitor_rtmidi_input(device_name)
        elif backend == 'mido':
            self._monitor_mido_input(device_name)
        elif backend == 'pygame':
            self._monitor_pygame_input(device_name)
    
    def _monitor_rtmidi_input(self, device_name):
        """Monitor MIDI input using rtmidi."""
        try:
            midi_in = rtmidi.MidiIn(name="MIDI_Monitor")
            
            # Find device
            device_id = None
            for i in range(midi_in.get_port_count()):
                port_name = midi_in.get_port_name(i)
                if device_name in port_name or port_name in device_name:
                    device_id = i
                    break
            
            if device_id is None:
                self.printer.error("Device not found for monitoring")
                return
            
            midi_in.open_port(device_id)
            midi_in.set_callback(self._rtmidi_callback)
            
            self.printer.success("Monitoring started. Press Ctrl+C to stop.")
            self._start_monitoring_loop()
            
            midi_in.close_port()
            
        except Exception as e:
            self.printer.error(f"rtmidi monitoring error: {e}")
    
    def _monitor_mido_input(self, device_name):
        """Monitor MIDI input using mido."""
        try:
            # Find exact device name
            available_inputs = mido.get_input_names()
            matching_device = None
            
            for device in available_inputs:
                if device_name in device or device in device_name:
                    matching_device = device
                    break
            
            if matching_device is None:
                self.printer.error("Device not found for monitoring")
                return
            
            with mido.open_input(matching_device) as inport:
                self.printer.success("Monitoring started. Press Ctrl+C to stop.")
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
            self.printer.error(f"mido monitoring error: {e}")
    
    def _monitor_pygame_input(self, device_name):
        """Monitor MIDI input using pygame."""
        try:
            pygame.midi.init()
            
            # Find device
            device_id = None
            for i in range(pygame.midi.get_count()):
                info = pygame.midi.get_device_info(i)
                name = info[1].decode('utf-8')
                is_input = info[2]
                
                if is_input and (device_name in name or name in device_name):
                    device_id = i
                    break
            
            if device_id is None:
                pygame.midi.quit()
                self.printer.error("Device not found for monitoring")
                return
            
            midi_input = pygame.midi.Input(device_id)
            self.printer.success("Monitoring started. Press Ctrl+C to stop.")
            
            self._start_pygame_monitoring_loop(midi_input)
            
            midi_input.close()
            pygame.midi.quit()
            
        except Exception as e:
            self.printer.error(f"pygame monitoring error: {e}")
            try:
                pygame.midi.quit()
            except:
                pass
    
    def _start_monitoring_loop(self):
        """Start the monitoring loop for rtmidi."""
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
    
    def _start_pygame_monitoring_loop(self, midi_input):
        """Start the monitoring loop for pygame."""
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
            self.printer.info(f"Stopped monitoring. Received {self.message_count} messages.")
    
    def _rtmidi_callback(self, event, data=None):
        """Callback for rtmidi messages."""
        message, deltatime = event
        self._process_raw_midi_message(message)
    
    def _process_mido_message(self, message):
        """Process a mido MIDI message."""
        self.message_count += 1
        formatted = format_midi_message(message)
        
        if message.type == 'note_on' and message.velocity > 0:
            note_name = note_number_to_name(message.note)
            velocity_bar = velocity_to_bar(message.velocity)
            self.printer.print_colored(
                f"♪ {formatted} ({note_name}) {velocity_bar}",
                'bright_green'
            )
        elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
            note_name = note_number_to_name(message.note)
            self.printer.print_colored(f"♪ {formatted} ({note_name})", 'yellow')
        else:
            self.printer.print_colored(f"► {formatted}", 'cyan')
    
    def _process_raw_midi_message(self, message):
        """Process raw MIDI message from rtmidi."""
        self.message_count += 1
        
        if len(message) >= 2:
            status = message[0]
            msg_type = status & 0xF0
            channel = (status & 0x0F) + 1
            
            if msg_type == 0x90 and len(message) >= 3:  # Note On
                note = message[1]
                velocity = message[2]
                if velocity > 0:
                    note_name = note_number_to_name(note)
                    velocity_bar = velocity_to_bar(velocity)
                    self.printer.print_colored(
                        f"♪ Note On - Ch:{channel} Note:{note} ({note_name}) Vel:{velocity} {velocity_bar}",
                        'bright_green'
                    )
                else:
                    note_name = note_number_to_name(note)
                    self.printer.print_colored(
                        f"♪ Note Off - Ch:{channel} Note:{note} ({note_name})",
                        'yellow'
                    )
            elif msg_type == 0x80 and len(message) >= 3:  # Note Off
                note = message[1]
                note_name = note_number_to_name(note)
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
    
    def _process_pygame_message(self, event):
        """Process pygame MIDI message."""
        self.message_count += 1
        midi_data, timestamp = event
        
        if len(midi_data) >= 2:
            status = midi_data[0]
            msg_type = status & 0xF0
            channel = (status & 0x0F) + 1
            
            if msg_type == 0x90 and len(midi_data) >= 3:  # Note On
                note = midi_data[1]
                velocity = midi_data[2]
                if velocity > 0:
                    note_name = note_number_to_name(note)
                    velocity_bar = velocity_to_bar(velocity)
                    self.printer.print_colored(
                        f"♪ Note On - Ch:{channel} Note:{note} ({note_name}) Vel:{velocity} {velocity_bar}",
                        'bright_green'
                    )
                else:
                    note_name = note_number_to_name(note)
                    self.printer.print_colored(
                        f"♪ Note Off - Ch:{channel} Note:{note} ({note_name})",
                        'yellow'
                    )
            elif msg_type == 0x80 and len(midi_data) >= 3:  # Note Off
                note = midi_data[1]
                note_name = note_number_to_name(note)
                self.printer.print_colored(
                    f"♪ Note Off - Ch:{channel} Note:{note} ({note_name})",
                    'yellow'
                )
            elif msg_type == 0xB0 and len(midi_data) >= 3:  # Control Change
                control = midi_data[1]
                value = midi_data[2]
                self.printer.print_colored(
                    f"► CC - Ch:{channel} Control:{control} Value:{value}",
                    'cyan'
                )
            else:
                self.printer.print_colored(f"► Raw MIDI: {list(midi_data)}", 'white')
    
    def _parse_device_string(self, device_string):
        """Parse device string to extract backend and device info."""
        try:
            if ':' in device_string:
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
            else:
                # Assume it's just a device name
                return None, None, device_string
                
        except Exception as e:
            self.printer.error(f"Error parsing device string: {e}")
        
        return None, None, device_string

def main():
    """Main function for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python advanced_input_tester.py <device_string>")
        print("Example: python advanced_input_tester.py 'rtmidi:0:SMC-Mixer-bt 0'")
        return
    
    device_string = sys.argv[1]
    tester = AdvancedMIDIInputTester()
    
    # First, test compatibility with all backends
    tester.test_device_all_backends(device_string)
    
    # If any backend works, offer to monitor with it
    if tester.successful_backends:
        response = input("\nWould you like to start monitoring with a working backend? (y/n): ")
        if response.lower() == 'y':
            tester.test_with_working_backend(device_string)

if __name__ == "__main__":
    main()
"""
MIDI Device Scanner - Detects and lists available MIDI input/output devices.
"""

import sys
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

try:
    import pygame
    import pygame.midi
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class MIDIDeviceScanner:
    """Scans for available MIDI devices using multiple backends."""
    
    def __init__(self):
        self.printer = ColorPrinter()
        self.backends_status = {
            'rtmidi': RTMIDI_AVAILABLE,
            'mido': MIDO_AVAILABLE,
            'pygame': PYGAME_AVAILABLE
        }
    
    def check_backend_availability(self):
        """Check which MIDI backends are available."""
        self.printer.print_header("MIDI Backend Availability")
        
        for backend, available in self.backends_status.items():
            if available:
                self.printer.success(f"{backend} - Available")
            else:
                self.printer.error(f"{backend} - Not Available")
        
        if not any(self.backends_status.values()):
            self.printer.error("No MIDI backends available! Please install python-rtmidi, mido, or pygame.")
            return False
        
        return True
    
    def scan_rtmidi_devices(self):
        """Scan devices using python-rtmidi."""
        if not RTMIDI_AVAILABLE:
            return [], []
        
        try:
            # Input devices
            midi_in = rtmidi.MidiIn()
            input_devices = []
            for i in range(midi_in.get_port_count()):
                port_name = midi_in.get_port_name(i)
                input_devices.append(f"rtmidi:{i}:{port_name}")
            midi_in.close_port()
            del midi_in
            
            # Output devices
            midi_out = rtmidi.MidiOut()
            output_devices = []
            for i in range(midi_out.get_port_count()):
                port_name = midi_out.get_port_name(i)
                output_devices.append(f"rtmidi:{i}:{port_name}")
            midi_out.close_port()
            del midi_out
            
            return input_devices, output_devices
            
        except Exception as e:
            self.printer.error(f"Error scanning rtmidi devices: {e}")
            return [], []
    
    def scan_mido_devices(self):
        """Scan devices using mido."""
        if not MIDO_AVAILABLE:
            return [], []
        
        try:
            input_devices = [f"mido:{name}" for name in mido.get_input_names()]
            output_devices = [f"mido:{name}" for name in mido.get_output_names()]
            return input_devices, output_devices
        except Exception as e:
            self.printer.error(f"Error scanning mido devices: {e}")
            return [], []
    
    def scan_pygame_devices(self):
        """Scan devices using pygame."""
        if not PYGAME_AVAILABLE:
            return [], []
        
        try:
            pygame.midi.init()
            input_devices = []
            output_devices = []
            
            for i in range(pygame.midi.get_count()):
                info = pygame.midi.get_device_info(i)
                name = info[1].decode('utf-8')
                is_input = info[2]
                is_output = info[3]
                
                if is_input:
                    input_devices.append(f"pygame:{i}:{name}")
                if is_output:
                    output_devices.append(f"pygame:{i}:{name}")
            
            pygame.midi.quit()
            return input_devices, output_devices
            
        except Exception as e:
            self.printer.error(f"Error scanning pygame devices: {e}")
            return [], []
    
    def get_all_devices(self):
        """Get all available MIDI devices from all backends."""
        all_input_devices = []
        all_output_devices = []
        
        # Scan with each available backend
        if self.backends_status['rtmidi']:
            input_devs, output_devs = self.scan_rtmidi_devices()
            all_input_devices.extend(input_devs)
            all_output_devices.extend(output_devs)
        
        if self.backends_status['mido']:
            input_devs, output_devs = self.scan_mido_devices()
            all_input_devices.extend(input_devs)
            all_output_devices.extend(output_devs)
        
        if self.backends_status['pygame']:
            input_devs, output_devs = self.scan_pygame_devices()
            all_input_devices.extend(input_devs)
            all_output_devices.extend(output_devs)
        
        return all_input_devices, all_output_devices
    
    def get_input_devices(self):
        """Get only input devices."""
        input_devices, _ = self.get_all_devices()
        return input_devices
    
    def get_output_devices(self):
        """Get only output devices."""
        _, output_devices = self.get_all_devices()
        return output_devices
    
    def scan_and_display_devices(self):
        """Scan and display all available MIDI devices."""
        if not self.check_backend_availability():
            return
        
        print()
        input_devices, output_devices = self.get_all_devices()
        
        # Display input devices
        self.printer.print_colored("MIDI INPUT DEVICES:", 'bright_green')
        if input_devices:
            for i, device in enumerate(input_devices):
                backend, device_info = device.split(':', 1)
                self.printer.print_colored(f"  {i:2d}. [{backend:>7}] {device_info}", 'green')
        else:
            self.printer.warning("  No MIDI input devices found")
        
        print()
        
        # Display output devices
        self.printer.print_colored("MIDI OUTPUT DEVICES:", 'bright_blue')
        if output_devices:
            for i, device in enumerate(output_devices):
                backend, device_info = device.split(':', 1)
                self.printer.print_colored(f"  {i:2d}. [{backend:>7}] {device_info}", 'blue')
        else:
            self.printer.warning("  No MIDI output devices found")
        
        print()
        
        # Summary
        total_devices = len(input_devices) + len(output_devices)
        if total_devices > 0:
            self.printer.success(f"Found {len(input_devices)} input and {len(output_devices)} output devices")
        else:
            self.printer.error("No MIDI devices found!")
            self.printer.info("Make sure MIDI devices are connected and drivers are installed")
    
    def get_device_details(self, device_string):
        """Parse device string and return backend and device info."""
        try:
            parts = device_string.split(':', 2)
            backend = parts[0]
            
            if backend == 'rtmidi':
                device_id = int(parts[1])
                device_name = parts[2] if len(parts) > 2 else f"Device {device_id}"
                return backend, device_id, device_name
            elif backend in ['mido', 'pygame']:
                device_name = ':'.join(parts[1:])
                return backend, None, device_name
            else:
                return None, None, device_string
        except Exception as e:
            self.printer.error(f"Error parsing device string: {e}")
            return None, None, device_string

if __name__ == "__main__":
    scanner = MIDIDeviceScanner()
    scanner.scan_and_display_devices()
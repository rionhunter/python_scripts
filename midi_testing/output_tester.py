"""
MIDI Output Tester - Tests MIDI output functionality by sending test messages.
"""

import time
from utils import ColorPrinter, note_number_to_name

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

class MIDIOutputTester:
    """Tests MIDI output functionality."""
    
    def __init__(self):
        self.printer = ColorPrinter()
    
    def test_device(self, device_string):
        """Test a specific MIDI output device."""
        backend, device_id, device_name = self._parse_device_string(device_string)
        
        if backend is None:
            self.printer.error("Invalid device string format")
            return
        
        self.printer.info(f"Testing device: {device_name} (backend: {backend})")
        
        print("\nSelect test to run:")
        print("1. Basic Note Test (C major scale)")
        print("2. Velocity Test (same note, different velocities)")
        print("3. Channel Test (notes on different channels)")
        print("4. Control Change Test")
        print("5. Program Change Test")
        print("6. Pitch Bend Test")
        print("7. Motorized Fader Test (all channels)")
        print("8. Light/LED Test (all channels)")
        print("9. Advanced Controller Test (faders + lights)")
        print("10. Comprehensive Test (all of the above)")
        print("11. Interactive Note Player")
        
        try:
            choice = int(input("Enter choice (1-11): "))
            
            if backend == 'rtmidi':
                self._test_rtmidi_output(device_id, choice)
            elif backend == 'mido':
                self._test_mido_output(device_name, choice)
            elif backend == 'pygame':
                self._test_pygame_output(device_id, choice)
            else:
                self.printer.error(f"Unsupported backend: {backend}")
                
        except ValueError:
            self.printer.error("Invalid choice. Please enter a number.")
    
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
    
    def _test_rtmidi_output(self, device_id, test_choice):
        """Test MIDI output using python-rtmidi."""
        if not RTMIDI_AVAILABLE:
            self.printer.error("python-rtmidi not available")
            return
        
        try:
            midi_out = rtmidi.MidiOut()
            
            if device_id >= midi_out.get_port_count():
                self.printer.error(f"Device ID {device_id} not found")
                return
            
            midi_out.open_port(device_id)
            self.printer.success("MIDI output opened successfully")
            
            self._run_output_test(test_choice, self._send_rtmidi_message, midi_out)
            
            midi_out.close_port()
            
        except Exception as e:
            self.printer.error(f"Error testing rtmidi output: {e}")
    
    def _test_mido_output(self, device_name, test_choice):
        """Test MIDI output using mido."""
        if not MIDO_AVAILABLE:
            self.printer.error("mido not available")
            return
        
        try:
            with mido.open_output(device_name) as outport:
                self.printer.success("MIDI output opened successfully")
                self._run_output_test(test_choice, self._send_mido_message, outport)
                
        except Exception as e:
            self.printer.error(f"Error testing mido output: {e}")
    
    def _test_pygame_output(self, device_id, test_choice):
        """Test MIDI output using pygame."""
        if not PYGAME_AVAILABLE:
            self.printer.error("pygame not available")
            return
        
        try:
            pygame.midi.init()
            
            if device_id >= pygame.midi.get_count():
                self.printer.error(f"Device ID {device_id} not found")
                return
            
            midi_output = pygame.midi.Output(device_id)
            self.printer.success("MIDI output opened successfully")
            
            self._run_output_test(test_choice, self._send_pygame_message, midi_output)
            
            midi_output.close()
            pygame.midi.quit()
            
        except Exception as e:
            self.printer.error(f"Error testing pygame output: {e}")
    
    def _run_output_test(self, test_choice, send_func, output_device):
        """Run the selected output test."""
        if test_choice == 1:
            self._test_basic_notes(send_func, output_device)
        elif test_choice == 2:
            self._test_velocity(send_func, output_device)
        elif test_choice == 3:
            self._test_channels(send_func, output_device)
        elif test_choice == 4:
            self._test_control_change(send_func, output_device)
        elif test_choice == 5:
            self._test_program_change(send_func, output_device)
        elif test_choice == 6:
            self._test_pitch_bend(send_func, output_device)
        elif test_choice == 7:
            self._test_motorized_faders(send_func, output_device)
        elif test_choice == 8:
            self._test_light_feedback(send_func, output_device)
        elif test_choice == 9:
            self._test_advanced_controller(send_func, output_device)
        elif test_choice == 10:
            self._test_comprehensive(send_func, output_device)
        elif test_choice == 11:
            self._interactive_note_player(send_func, output_device)
        else:
            self.printer.error("Invalid test choice")
    
    def _test_basic_notes(self, send_func, output_device):
        """Test basic note on/off messages with C major scale."""
        self.printer.info("Testing basic notes (C major scale)...")
        
        # C major scale: C, D, E, F, G, A, B, C
        notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C4 to C5
        
        for note in notes:
            note_name = note_number_to_name(note)
            self.printer.print_colored(f"Playing {note_name} (MIDI note {note})", 'green')
            
            # Note on
            send_func(output_device, 'note_on', 0, note, 100)
            time.sleep(0.5)
            
            # Note off
            send_func(output_device, 'note_off', 0, note, 0)
            time.sleep(0.1)
        
        self.printer.success("Basic note test completed")
    
    def _test_velocity(self, send_func, output_device):
        """Test velocity sensitivity."""
        self.printer.info("Testing velocity sensitivity...")
        
        note = 60  # Middle C
        velocities = [32, 64, 96, 127]
        
        for vel in velocities:
            self.printer.print_colored(f"Playing C4 with velocity {vel}", 'yellow')
            
            send_func(output_device, 'note_on', 0, note, vel)
            time.sleep(0.8)
            send_func(output_device, 'note_off', 0, note, 0)
            time.sleep(0.2)
        
        self.printer.success("Velocity test completed")
    
    def _test_channels(self, send_func, output_device):
        """Test different MIDI channels."""
        self.printer.info("Testing different MIDI channels...")
        
        note = 60  # Middle C
        channels = [0, 1, 2, 9]  # Including channel 10 (drums)
        
        for channel in channels:
            self.printer.print_colored(f"Playing C4 on channel {channel + 1}", 'cyan')
            
            send_func(output_device, 'note_on', channel, note, 100)
            time.sleep(0.5)
            send_func(output_device, 'note_off', channel, note, 0)
            time.sleep(0.2)
        
        self.printer.success("Channel test completed")
    
    def _test_control_change(self, send_func, output_device):
        """Test control change messages."""
        self.printer.info("Testing control change messages...")
        
        # Test volume control (CC 7)
        self.printer.print_colored("Testing volume control (CC 7)", 'magenta')
        
        # Play a sustained note while changing volume
        send_func(output_device, 'note_on', 0, 60, 100)
        
        for volume in [127, 64, 32, 127]:
            self.printer.print_colored(f"Setting volume to {volume}", 'magenta')
            send_func(output_device, 'control_change', 0, 7, volume)
            time.sleep(0.5)
        
        send_func(output_device, 'note_off', 0, 60, 0)
        
        # Test modulation wheel (CC 1)
        self.printer.print_colored("Testing modulation wheel (CC 1)", 'magenta')
        
        send_func(output_device, 'note_on', 0, 60, 100)
        
        for mod_value in [0, 64, 127, 0]:
            self.printer.print_colored(f"Setting modulation to {mod_value}", 'magenta')
            send_func(output_device, 'control_change', 0, 1, mod_value)
            time.sleep(0.5)
        
        send_func(output_device, 'note_off', 0, 60, 0)
        
        self.printer.success("Control change test completed")
    
    def _test_program_change(self, send_func, output_device):
        """Test program change messages."""
        self.printer.info("Testing program change messages...")
        
        programs = [0, 1, 24, 40]  # Piano, Bright Piano, Guitar, Violin
        program_names = ["Piano", "Bright Piano", "Guitar", "Violin"]
        
        note = 60
        
        for program, name in zip(programs, program_names):
            self.printer.print_colored(f"Switching to program {program} ({name})", 'blue')
            
            send_func(output_device, 'program_change', 0, program, None)
            time.sleep(0.2)
            
            # Play a note with the new program
            send_func(output_device, 'note_on', 0, note, 100)
            time.sleep(0.8)
            send_func(output_device, 'note_off', 0, note, 0)
            time.sleep(0.2)
        
        self.printer.success("Program change test completed")
    
    def _test_pitch_bend(self, send_func, output_device):
        """Test pitch bend messages."""
        self.printer.info("Testing pitch bend...")
        
        # Play a sustained note while bending pitch
        send_func(output_device, 'note_on', 0, 60, 100)
        
        # Pitch bend values: 0x2000 = center (no bend)
        bend_values = [0x2000, 0x3000, 0x4000, 0x2000, 0x1000, 0x0000, 0x2000]
        
        for bend_value in bend_values:
            self.printer.print_colored(f"Pitch bend: {bend_value:04X}", 'red')
            send_func(output_device, 'pitch_bend', 0, bend_value, None)
            time.sleep(0.3)
        
        send_func(output_device, 'note_off', 0, 60, 0)
        
        self.printer.success("Pitch bend test completed")
    
    def _test_motorized_faders(self, send_func, output_device):
        """Test motorized faders by sending fader position feedback to all channels."""
        self.printer.info("Testing motorized faders (all channels)...")
        self.printer.info("Sending fader position feedback - watch for motorized fader movement")
        
        # Common MIDI CC numbers for motorized faders
        fader_ccs = [
            0,   # Bank Select MSB (some controllers use this)
            1,   # Modulation Wheel (often mapped to faders)
            7,   # Volume (most common for faders)
            10,  # Pan
            11,  # Expression
            14,  # Controller 14 (often used for faders)
            15,  # Controller 15 (often used for faders)
            16,  # Controller 16 (often used for faders)
            17,  # Controller 17 (often used for faders)
            18,  # Controller 18 (often used for faders)
            19,  # Controller 19 (often used for faders)
            20,  # Controller 20 (often used for faders)
            21,  # Controller 21 (often used for faders)
        ]
        
        # Test on all 16 MIDI channels
        for channel in range(16):
            self.printer.print_colored(f"Testing motorized faders on Channel {channel + 1}", 'cyan')
            
            # Test different fader CC numbers
            for cc_num in fader_ccs:
                # Send fader positions from 0 to 127 and back
                positions = [0, 32, 64, 96, 127, 96, 64, 32, 0]
                
                for position in positions:
                    self.printer.print_colored(f"  Ch{channel + 1:2d} CC{cc_num:2d}: Position {position:3d}", 'green')
                    send_func(output_device, 'control_change', channel, cc_num, position)
                    time.sleep(0.1)  # Short delay to see movement
            
            time.sleep(0.2)  # Pause between channels
        
        # Reset all faders to center position
        self.printer.info("Resetting all faders to center position (64)...")
        for channel in range(16):
            for cc_num in fader_ccs:
                send_func(output_device, 'control_change', channel, cc_num, 64)
        
        self.printer.success("Motorized fader test completed")
    
    def _test_light_feedback(self, send_func, output_device):
        """Test LED/light feedback by sending button states to all channels."""
        self.printer.info("Testing LED/Light feedback (all channels)...")
        self.printer.info("Sending button/pad states - watch for LED changes")
        
        # Common MIDI patterns for LED feedback
        led_tests = [
            # Note-based LED feedback (common for drum pads and button matrices)
            ("Note-based LEDs", "note", range(36, 84)),  # Drum pad range
            # Control Change based LED feedback
            ("CC-based LEDs", "cc", range(64, 80)),      # Common CC range for buttons
            # Program Change based LED feedback  
            ("Program LEDs", "program", range(0, 16)),   # Program buttons
        ]
        
        for test_name, test_type, value_range in led_tests:
            self.printer.print_colored(f"\n{test_name}:", 'yellow')
            
            # Test on all 16 MIDI channels
            for channel in range(16):
                self.printer.print_colored(f"  Channel {channel + 1}:", 'cyan')
                
                # Light up sequence
                for value in list(value_range)[:8]:  # Limit to first 8 to avoid spam
                    if test_type == "note":
                        self.printer.print_colored(f"    Note {value} ON", 'green')
                        send_func(output_device, 'note_on', channel, value, 127)  # Full velocity for bright LED
                        time.sleep(0.1)
                        
                        self.printer.print_colored(f"    Note {value} OFF", 'red')
                        send_func(output_device, 'note_off', channel, value, 0)
                        time.sleep(0.1)
                        
                    elif test_type == "cc":
                        self.printer.print_colored(f"    CC {value} ON (127)", 'green')
                        send_func(output_device, 'control_change', channel, value, 127)
                        time.sleep(0.1)
                        
                        self.printer.print_colored(f"    CC {value} OFF (0)", 'red')
                        send_func(output_device, 'control_change', channel, value, 0)
                        time.sleep(0.1)
                        
                    elif test_type == "program":
                        self.printer.print_colored(f"    Program {value}", 'magenta')
                        send_func(output_device, 'program_change', channel, value, None)
                        time.sleep(0.2)
                
                time.sleep(0.3)  # Pause between channels
        
        # RGB LED test (if supported)
        self.printer.print_colored("\nRGB LED Test (Novation/AKAI style):", 'yellow')
        rgb_colors = [
            (127, 0, 0),    # Red
            (0, 127, 0),    # Green  
            (0, 0, 127),    # Blue
            (127, 127, 0),  # Yellow
            (127, 0, 127),  # Magenta
            (0, 127, 127),  # Cyan
            (127, 127, 127) # White
        ]
        
        for channel in range(4):  # Test first 4 channels for RGB
            for i, (r, g, b) in enumerate(rgb_colors):
                note = 36 + i  # Standard drum pad notes
                # Some controllers use velocity for color (simplified RGB)
                color_velocity = min(127, (r + g + b) // 3)
                self.printer.print_colored(f"  Ch{channel + 1} Note{note} RGB({r},{g},{b}) Vel:{color_velocity}", 'bright_magenta')
                send_func(output_device, 'note_on', channel, note, color_velocity)
                time.sleep(0.2)
                send_func(output_device, 'note_off', channel, note, 0)
        
        self.printer.success("Light/LED feedback test completed")
    
    def _test_advanced_controller(self, send_func, output_device):
        """Test advanced controller features combining faders and lights."""
        self.printer.info("Testing advanced controller features...")
        self.printer.info("Combining motorized faders with LED feedback")
        
        # Simulate a mixing console scenario
        channels_to_test = 8  # Test first 8 channels
        
        self.printer.print_colored("Simulating mixing console scenario:", 'bright_yellow')
        
        for channel in range(channels_to_test):
            self.printer.print_colored(f"\nChannel {channel + 1} automation:", 'cyan')
            
            # Simulate fader automation with LED feedback
            fader_sequence = [0, 32, 64, 96, 127, 96, 64, 32, 0]
            
            for i, fader_pos in enumerate(fader_sequence):
                # Set fader position (CC 7 = Volume)
                send_func(output_device, 'control_change', channel, 7, fader_pos)
                
                # Set corresponding LED brightness based on fader position
                led_velocity = fader_pos
                led_note = 36 + channel  # Map to drum pad LEDs
                
                if led_velocity > 0:
                    send_func(output_device, 'note_on', channel, led_note, led_velocity)
                    self.printer.print_colored(f"  Fader: {fader_pos:3d}, LED: ON ({led_velocity})", 'green')
                else:
                    send_func(output_device, 'note_off', channel, led_note, 0)
                    self.printer.print_colored(f"  Fader: {fader_pos:3d}, LED: OFF", 'red')
                
                time.sleep(0.3)
            
            # Turn off channel LED
            send_func(output_device, 'note_off', channel, 36 + channel, 0)
        
        # Master section test
        self.printer.print_colored("\nMaster section test:", 'bright_yellow')
        
        # Master fader sweep
        for master_level in [0, 32, 64, 96, 127]:
            # Set master fader on channel 16 (often used for master)
            send_func(output_device, 'control_change', 15, 7, master_level)
            
            # Light up multiple LEDs to indicate master level
            num_leds = (master_level // 16) + 1  # 1-8 LEDs based on level
            
            for led in range(8):
                if led < num_leds:
                    send_func(output_device, 'note_on', 15, 36 + led, 127)
                else:
                    send_func(output_device, 'note_off', 15, 36 + led, 0)
            
            self.printer.print_colored(f"Master level: {master_level:3d}, LEDs: {num_leds}", 'yellow')
            time.sleep(0.5)
        
        # Transport control test
        self.printer.print_colored("\nTransport control test:", 'bright_yellow')
        transport_buttons = [
            (91, "Play"),
            (92, "Stop"), 
            (93, "Record"),
            (94, "Rewind"),
            (95, "Fast Forward")
        ]
        
        for cc_num, name in transport_buttons:
            # Button press (LED on)
            send_func(output_device, 'control_change', 0, cc_num, 127)
            self.printer.print_colored(f"{name} button: ON", 'green')
            time.sleep(0.5)
            
            # Button release (LED off)
            send_func(output_device, 'control_change', 0, cc_num, 0)
            self.printer.print_colored(f"{name} button: OFF", 'red')
            time.sleep(0.3)
        
        # Reset all controls
        self.printer.info("Resetting all controls...")
        for channel in range(16):
            # Reset faders to 0
            send_func(output_device, 'control_change', channel, 7, 0)
            # Turn off all LEDs
            for note in range(36, 44):
                send_func(output_device, 'note_off', channel, note, 0)
        
        self.printer.success("Advanced controller test completed")
    
    def _test_comprehensive(self, send_func, output_device):
        """Run all tests in sequence."""
        self.printer.info("Running comprehensive test suite...")
        
        tests = [
            ("Basic Notes", self._test_basic_notes),
            ("Velocity", self._test_velocity),
            ("Channels", self._test_channels),
            ("Control Change", self._test_control_change),
            ("Program Change", self._test_program_change),
            ("Pitch Bend", self._test_pitch_bend),
            ("Motorized Faders", self._test_motorized_faders),
            ("Light/LED Feedback", self._test_light_feedback),
            ("Advanced Controller", self._test_advanced_controller)
        ]
        
        for test_name, test_func in tests:
            self.printer.print_colored(f"\n--- {test_name} Test ---", 'bright_yellow')
            test_func(send_func, output_device)
            time.sleep(1)
        
        self.printer.success("Comprehensive test completed!")
    
    def _interactive_note_player(self, send_func, output_device):
        """Interactive note player."""
        self.printer.info("Interactive Note Player")
        self.printer.info("Enter MIDI note numbers (0-127) or 'q' to quit")
        self.printer.info("Examples: 60 (Middle C), 69 (A4), 72 (C5)")
        
        while True:
            try:
                user_input = input("Note number: ").strip().lower()
                
                if user_input == 'q':
                    break
                
                note = int(user_input)
                
                if 0 <= note <= 127:
                    note_name = note_number_to_name(note)
                    self.printer.print_colored(f"Playing {note_name} (MIDI note {note})", 'green')
                    
                    send_func(output_device, 'note_on', 0, note, 100)
                    time.sleep(0.5)
                    send_func(output_device, 'note_off', 0, note, 0)
                else:
                    self.printer.error("Note number must be between 0 and 127")
                    
            except ValueError:
                self.printer.error("Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                break
        
        self.printer.info("Interactive player stopped")
    
    def _send_rtmidi_message(self, output_device, msg_type, channel, data1, data2):
        """Send MIDI message using rtmidi."""
        if msg_type == 'note_on':
            message = [0x90 | channel, data1, data2]
        elif msg_type == 'note_off':
            message = [0x80 | channel, data1, data2]
        elif msg_type == 'control_change':
            message = [0xB0 | channel, data1, data2]
        elif msg_type == 'program_change':
            message = [0xC0 | channel, data1]
        elif msg_type == 'pitch_bend':
            lsb = data1 & 0x7F
            msb = (data1 >> 7) & 0x7F
            message = [0xE0 | channel, lsb, msb]
        else:
            return
        
        output_device.send_message(message)
    
    def _send_mido_message(self, output_device, msg_type, channel, data1, data2):
        """Send MIDI message using mido."""
        if msg_type == 'note_on':
            msg = mido.Message('note_on', channel=channel, note=data1, velocity=data2)
        elif msg_type == 'note_off':
            msg = mido.Message('note_off', channel=channel, note=data1, velocity=data2)
        elif msg_type == 'control_change':
            msg = mido.Message('control_change', channel=channel, control=data1, value=data2)
        elif msg_type == 'program_change':
            msg = mido.Message('program_change', channel=channel, program=data1)
        elif msg_type == 'pitch_bend':
            msg = mido.Message('pitchwheel', channel=channel, pitch=data1)
        else:
            return
        
        output_device.send(msg)
    
    def _send_pygame_message(self, output_device, msg_type, channel, data1, data2):
        """Send MIDI message using pygame."""
        if msg_type == 'note_on':
            output_device.note_on(data1, data2, channel)
        elif msg_type == 'note_off':
            output_device.note_off(data1, data2, channel)
        elif msg_type == 'control_change':
            # pygame doesn't have direct CC support, use raw message
            message = [0xB0 | channel, data1, data2, 0]
            output_device.write([message])
        elif msg_type == 'program_change':
            output_device.set_instrument(data1, channel)
        elif msg_type == 'pitch_bend':
            lsb = data1 & 0x7F
            msb = (data1 >> 7) & 0x7F
            message = [0xE0 | channel, lsb, msb, 0]
            output_device.write([message])

if __name__ == "__main__":
    from device_scanner import MIDIDeviceScanner
    
    tester = MIDIOutputTester()
    scanner = MIDIDeviceScanner()
    
    output_devices = scanner.get_output_devices()
    if output_devices:
        print("Available output devices:")
        for i, device in enumerate(output_devices):
            print(f"{i}: {device}")
        
        choice = int(input(f"Select device (0-{len(output_devices)-1}): "))
        if 0 <= choice < len(output_devices):
            tester.test_device(output_devices[choice])
    else:
        print("No MIDI output devices found!")
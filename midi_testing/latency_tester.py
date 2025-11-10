"""
MIDI Latency Tester - Measures MIDI round-trip latency and timing accuracy.
"""

import time
import threading
import statistics
from utils import ColorPrinter, format_time

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

class MIDILatencyTester:
    """Tests MIDI latency and timing accuracy."""
    
    def __init__(self):
        self.printer = ColorPrinter()
        self.test_results = []
        self.waiting_for_response = False
        self.send_time = 0
        self.response_received = False
    
    def run_latency_test(self):
        """Run a comprehensive latency test."""
        from device_scanner import MIDIDeviceScanner
        
        scanner = MIDIDeviceScanner()
        input_devices = scanner.get_input_devices()
        output_devices = scanner.get_output_devices()
        
        if not input_devices or not output_devices:
            self.printer.error("Both input and output devices are required for latency testing")
            return
        
        print("MIDI Latency Testing")
        print("===================")
        print("This test measures the time it takes for a MIDI message to be sent")
        print("and received back through your MIDI setup.")
        print()
        
        # Select devices
        print("Select INPUT device:")
        for i, device in enumerate(input_devices):
            print(f"{i}: {device}")
        
        try:
            input_choice = int(input(f"Input device (0-{len(input_devices)-1}): "))
            if not (0 <= input_choice < len(input_devices)):
                self.printer.error("Invalid input device selection")
                return
        except ValueError:
            self.printer.error("Invalid input")
            return
        
        print("\nSelect OUTPUT device:")
        for i, device in enumerate(output_devices):
            print(f"{i}: {device}")
        
        try:
            output_choice = int(input(f"Output device (0-{len(output_devices)-1}): "))
            if not (0 <= output_choice < len(output_devices)):
                self.printer.error("Invalid output device selection")
                return
        except ValueError:
            self.printer.error("Invalid input")
            return
        
        input_device = input_devices[input_choice]
        output_device = output_devices[output_choice]
        
        print(f"\nTesting latency between:")
        print(f"Output: {output_device}")
        print(f"Input:  {input_device}")
        print()
        
        # Run test
        self._run_roundtrip_test(input_device, output_device)
    
    def _run_roundtrip_test(self, input_device_str, output_device_str):
        """Run round-trip latency test."""
        # Parse device strings
        input_backend, input_id, input_name = self._parse_device_string(input_device_str)
        output_backend, output_id, output_name = self._parse_device_string(output_device_str)
        
        if input_backend is None or output_backend is None:
            self.printer.error("Invalid device format")
            return
        
        # For now, only support mido for latency testing (most reliable)
        if MIDO_AVAILABLE:
            self._run_mido_latency_test(input_name, output_name)
        elif RTMIDI_AVAILABLE:
            self._run_rtmidi_latency_test(input_id, output_id)
        else:
            self.printer.error("No suitable MIDI backend available for latency testing")
    
    def _run_mido_latency_test(self, input_name, output_name):
        """Run latency test using mido."""
        try:
            with mido.open_input(input_name) as inport, mido.open_output(output_name) as outport:
                self.printer.success("MIDI ports opened successfully")
                
                # Instructions
                print("Latency Test Instructions:")
                print("1. Connect the MIDI output to MIDI input (loopback)")
                print("2. The test will send MIDI messages and measure response time")
                print("3. Press Enter to start the test...")
                
                input()
                
                self.printer.info("Starting latency test...")
                print("Sending test messages...")
                
                self.test_results = []
                
                # Test parameters
                num_tests = 20
                test_note = 60
                test_velocity = 100
                
                for i in range(num_tests):
                    print(f"Test {i+1}/{num_tests}...", end=' ')
                    
                    # Clear any pending messages
                    while inport.poll():
                        inport.receive()
                    
                    # Send message and measure time
                    self.response_received = False
                    send_time = time.perf_counter()
                    
                    # Send note on message
                    msg = mido.Message('note_on', note=test_note, velocity=test_velocity)
                    outport.send(msg)
                    
                    # Wait for response with timeout
                    timeout = 1.0  # 1 second timeout
                    start_wait = time.perf_counter()
                    
                    while not self.response_received and (time.perf_counter() - start_wait) < timeout:
                        if inport.poll():
                            received_msg = inport.receive()
                            receive_time = time.perf_counter()
                            
                            # Check if this is our test message
                            if (received_msg.type == 'note_on' and 
                                received_msg.note == test_note and
                                received_msg.velocity == test_velocity):
                                
                                latency = (receive_time - send_time) * 1000  # Convert to ms
                                self.test_results.append(latency)
                                self.response_received = True
                                
                                print(f"✓ {latency:.2f}ms")
                                break
                    
                    if not self.response_received:
                        print("✗ Timeout")
                    
                    # Send note off to clean up
                    msg_off = mido.Message('note_off', note=test_note, velocity=0)
                    outport.send(msg_off)
                    
                    time.sleep(0.1)  # Small delay between tests
                
                self._analyze_results()
                
        except Exception as e:
            self.printer.error(f"Error during mido latency test: {e}")
    
    def _run_rtmidi_latency_test(self, input_id, output_id):
        """Run latency test using rtmidi."""
        try:
            midi_in = rtmidi.MidiIn()
            midi_out = rtmidi.MidiOut()
            
            if input_id >= midi_in.get_port_count() or output_id >= midi_out.get_port_count():
                self.printer.error("Device not found")
                return
            
            midi_in.open_port(input_id)
            midi_out.open_port(output_id)
            
            # Set up callback
            midi_in.set_callback(self._rtmidi_latency_callback)
            
            self.printer.success("MIDI ports opened successfully")
            
            print("Latency Test Instructions:")
            print("1. Connect the MIDI output to MIDI input (loopback)")
            print("2. Press Enter to start the test...")
            
            input()
            
            self.printer.info("Starting latency test...")
            
            self.test_results = []
            num_tests = 20
            
            for i in range(num_tests):
                print(f"Test {i+1}/{num_tests}...", end=' ')
                
                self.response_received = False
                self.send_time = time.perf_counter()
                
                # Send note on message
                note_on = [0x90, 60, 100]  # Note on, middle C, velocity 100
                midi_out.send_message(note_on)
                
                # Wait for response
                timeout = 1.0
                start_wait = time.perf_counter()
                
                while not self.response_received and (time.perf_counter() - start_wait) < timeout:
                    time.sleep(0.001)  # Small sleep to prevent busy waiting
                
                if not self.response_received:
                    print("✗ Timeout")
                
                # Send note off
                note_off = [0x80, 60, 0]
                midi_out.send_message(note_off)
                
                time.sleep(0.1)
            
            midi_in.close_port()
            midi_out.close_port()
            
            self._analyze_results()
            
        except Exception as e:
            self.printer.error(f"Error during rtmidi latency test: {e}")
    
    def _rtmidi_latency_callback(self, event, data=None):
        """Callback for rtmidi latency testing."""
        message, deltatime = event
        
        if len(message) >= 3 and message[0] == 0x90 and message[1] == 60:  # Note on, middle C
            receive_time = time.perf_counter()
            latency = (receive_time - self.send_time) * 1000  # Convert to ms
            self.test_results.append(latency)
            self.response_received = True
            print(f"✓ {latency:.2f}ms")
    
    def _analyze_results(self):
        """Analyze and display latency test results."""
        if not self.test_results:
            self.printer.error("No successful latency measurements obtained")
            return
        
        print(f"\nLatency Test Results ({len(self.test_results)} successful measurements):")
        print("=" * 60)
        
        # Calculate statistics
        min_latency = min(self.test_results)
        max_latency = max(self.test_results)
        avg_latency = statistics.mean(self.test_results)
        median_latency = statistics.median(self.test_results)
        
        if len(self.test_results) > 1:
            stdev_latency = statistics.stdev(self.test_results)
        else:
            stdev_latency = 0
        
        # Display statistics
        self.printer.print_colored(f"Minimum Latency:  {min_latency:8.2f} ms", 'green')
        self.printer.print_colored(f"Maximum Latency:  {max_latency:8.2f} ms", 'red')
        self.printer.print_colored(f"Average Latency:  {avg_latency:8.2f} ms", 'yellow')
        self.printer.print_colored(f"Median Latency:   {median_latency:8.2f} ms", 'cyan')
        self.printer.print_colored(f"Std Deviation:    {stdev_latency:8.2f} ms", 'magenta')
        
        print()
        
        # Performance assessment
        if avg_latency < 5:
            self.printer.success("Excellent latency - suitable for real-time performance")
        elif avg_latency < 10:
            self.printer.success("Good latency - suitable for most applications")
        elif avg_latency < 20:
            self.printer.warning("Moderate latency - may be noticeable in some applications")
        else:
            self.printer.error("High latency - may cause timing issues")
        
        # Jitter assessment
        if stdev_latency < 2:
            self.printer.success("Low jitter - consistent timing")
        elif stdev_latency < 5:
            self.printer.warning("Moderate jitter - some timing variation")
        else:
            self.printer.error("High jitter - inconsistent timing")
        
        # Show histogram if we have enough data
        if len(self.test_results) >= 10:
            self._show_latency_histogram()
    
    def _show_latency_histogram(self):
        """Show a simple text histogram of latency results."""
        print(f"\nLatency Distribution:")
        print("-" * 40)
        
        # Create bins
        min_val = min(self.test_results)
        max_val = max(self.test_results)
        range_val = max_val - min_val
        
        if range_val > 0:
            num_bins = min(10, len(self.test_results) // 2)
            bin_size = range_val / num_bins
            bins = [0] * num_bins
            
            # Fill bins
            for result in self.test_results:
                bin_index = min(int((result - min_val) / bin_size), num_bins - 1)
                bins[bin_index] += 1
            
            # Display histogram
            max_count = max(bins)
            bar_width = 30
            
            for i, count in enumerate(bins):
                bin_start = min_val + i * bin_size
                bin_end = min_val + (i + 1) * bin_size
                bar_length = int((count / max_count) * bar_width) if max_count > 0 else 0
                bar = '█' * bar_length
                
                print(f"{bin_start:6.1f}-{bin_end:6.1f}ms: {bar} ({count})")
    
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

if __name__ == "__main__":
    tester = MIDILatencyTester()
    tester.run_latency_test()
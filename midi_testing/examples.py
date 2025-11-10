"""
Example usage of the MIDI Testing Suite
"""

import sys
from pathlib import Path

# Add the midi_testing directory to the path
sys.path.append(str(Path(__file__).parent))

from device_scanner import MIDIDeviceScanner
from input_tester import MIDIInputTester
from output_tester import MIDIOutputTester
from latency_tester import MIDILatencyTester
from pipeline_diagnostics import MIDIPipelineDiagnostics
from utils import ColorPrinter

def example_device_scan():
    """Example: Scan for MIDI devices"""
    print("=== Device Scanning Example ===")
    scanner = MIDIDeviceScanner()
    scanner.scan_and_display_devices()
    
    # Get devices programmatically
    input_devices = scanner.get_input_devices()
    output_devices = scanner.get_output_devices()
    
    print(f"\nFound {len(input_devices)} input devices and {len(output_devices)} output devices")

def example_quick_diagnostic():
    """Example: Quick system diagnostic"""
    print("\n=== Quick Diagnostic Example ===")
    diagnostics = MIDIPipelineDiagnostics()
    
    # Run individual checks
    diagnostics._check_system_info()
    diagnostics._check_midi_libraries()
    diagnostics._check_midi_devices()

def example_programmatic_testing():
    """Example: Programmatic testing without user interaction"""
    print("\n=== Programmatic Testing Example ===")
    
    printer = ColorPrinter()
    
    # Check if we have MIDI devices
    scanner = MIDIDeviceScanner()
    input_devices = scanner.get_input_devices()
    output_devices = scanner.get_output_devices()
    
    if input_devices:
        printer.success(f"Input devices available: {len(input_devices)}")
        # You could automatically test the first device
        # input_tester = MIDIInputTester()
        # input_tester.test_device(input_devices[0])
    else:
        printer.warning("No input devices found")
    
    if output_devices:
        printer.success(f"Output devices available: {len(output_devices)}")
        # You could automatically test the first device
        # output_tester = MIDIOutputTester()
        # output_tester.test_device(output_devices[0])
    else:
        printer.warning("No output devices found")

def example_integration_test():
    """Example: Integration test for a MIDI application"""
    print("\n=== Integration Test Example ===")
    
    printer = ColorPrinter()
    
    # This is how you might test MIDI functionality in your application
    steps = [
        "Check MIDI libraries are available",
        "Scan for required MIDI devices", 
        "Test device connections",
        "Verify MIDI message handling",
        "Measure latency if required"
    ]
    
    for i, step in enumerate(steps, 1):
        printer.info(f"Step {i}: {step}")
        # Here you would add actual test code
        # For now, we'll just simulate
        import time
        time.sleep(0.5)
        printer.success(f"✓ Step {i} completed")
    
    printer.success("Integration test completed successfully!")

if __name__ == "__main__":
    printer = ColorPrinter()
    printer.print_header("MIDI Testing Suite Examples")
    
    print("This script demonstrates various ways to use the MIDI Testing Suite")
    print("in your own applications.\n")
    
    # Run examples
    example_device_scan()
    example_quick_diagnostic()
    example_programmatic_testing()
    example_integration_test()
    
    print("\n" + "="*60)
    print("For interactive testing, run: python midi_test_suite.py")
    print("For full documentation, see: README.md")
    print("="*60)
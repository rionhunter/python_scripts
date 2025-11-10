"""
MIDI Testing Suite
==================

A comprehensive suite for testing MIDI input/output functionality and diagnosing
issues in MIDI pipelines. This tool helps identify where problems occur when
creating applications that use MIDI.

Components:
- Device Detection: List available MIDI devices
- Input Testing: Monitor MIDI input in real-time
- Output Testing: Send test MIDI messages
- Latency Testing: Measure MIDI round-trip latency
- Connection Testing: Test MIDI connections
- Pipeline Diagnostics: Comprehensive system analysis

Usage:
    python midi_test_suite.py --help
    python midi_test_suite.py --list-devices
    python midi_test_suite.py --test-input
    python midi_test_suite.py --test-output
    python midi_test_suite.py --latency-test
    python midi_test_suite.py --full-diagnostic
"""

import argparse
import sys
import time
import threading
from pathlib import Path

# Add the midi_testing directory to the path
sys.path.append(str(Path(__file__).parent))

from device_scanner import MIDIDeviceScanner
from input_tester import MIDIInputTester
from output_tester import MIDIOutputTester
from latency_tester import MIDILatencyTester
from pipeline_diagnostics import MIDIPipelineDiagnostics
from utils import ColorPrinter, clear_screen

class MIDITestSuite:
    def __init__(self):
        self.printer = ColorPrinter()
        self.device_scanner = MIDIDeviceScanner()
        self.input_tester = MIDIInputTester()
        self.output_tester = MIDIOutputTester()
        self.latency_tester = MIDILatencyTester()
        self.diagnostics = MIDIPipelineDiagnostics()
    
    def run_interactive_menu(self):
        """Run an interactive menu for testing various MIDI functions."""
        while True:
            clear_screen()
            self.printer.print_header("MIDI Testing Suite - Interactive Mode")
            
            print("Select a test to run:")
            print("1. List MIDI Devices")
            print("2. Test MIDI Input")
            print("3. Test MIDI Output")
            print("4. Latency Test")
            print("5. Full Pipeline Diagnostics")
            print("6. Connection Test")
            print("7. Real-time Monitor")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-7): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.list_devices()
            elif choice == '2':
                self.test_input()
            elif choice == '3':
                self.test_output()
            elif choice == '4':
                self.latency_test()
            elif choice == '5':
                self.full_diagnostic()
            elif choice == '6':
                self.connection_test()
            elif choice == '7':
                self.real_time_monitor()
            else:
                self.printer.error("Invalid choice. Please try again.")
            
            if choice != '0':
                input("\nPress Enter to continue...")
    
    def list_devices(self):
        """List all available MIDI devices."""
        clear_screen()
        self.printer.print_header("MIDI Device Scanner")
        self.device_scanner.scan_and_display_devices()
    
    def test_input(self):
        """Test MIDI input functionality."""
        clear_screen()
        self.printer.print_header("MIDI Input Tester")
        devices = self.device_scanner.get_input_devices()
        
        if not devices:
            self.printer.error("No MIDI input devices found!")
            return
        
        print("Available input devices:")
        for i, device in enumerate(devices):
            print(f"{i}: {device}")
        
        try:
            choice = int(input(f"\nSelect device (0-{len(devices)-1}): "))
            if 0 <= choice < len(devices):
                self.input_tester.test_device(devices[choice])
            else:
                self.printer.error("Invalid device selection.")
        except ValueError:
            self.printer.error("Invalid input. Please enter a number.")
    
    def test_output(self):
        """Test MIDI output functionality."""
        clear_screen()
        self.printer.print_header("MIDI Output Tester")
        devices = self.device_scanner.get_output_devices()
        
        if not devices:
            self.printer.error("No MIDI output devices found!")
            return
        
        print("Available output devices:")
        for i, device in enumerate(devices):
            print(f"{i}: {device}")
        
        try:
            choice = int(input(f"\nSelect device (0-{len(devices)-1}): "))
            if 0 <= choice < len(devices):
                self.output_tester.test_device(devices[choice])
            else:
                self.printer.error("Invalid device selection.")
        except ValueError:
            self.printer.error("Invalid input. Please enter a number.")
    
    def latency_test(self):
        """Run MIDI latency test."""
        clear_screen()
        self.printer.print_header("MIDI Latency Tester")
        self.latency_tester.run_latency_test()
    
    def full_diagnostic(self):
        """Run comprehensive MIDI pipeline diagnostics."""
        clear_screen()
        self.printer.print_header("Full MIDI Pipeline Diagnostics")
        self.diagnostics.run_full_diagnostic()
    
    def connection_test(self):
        """Test MIDI connections."""
        clear_screen()
        self.printer.print_header("MIDI Connection Tester")
        self.diagnostics.test_connections()
    
    def real_time_monitor(self):
        """Run real-time MIDI monitor."""
        clear_screen()
        self.printer.print_header("Real-time MIDI Monitor")
        self.input_tester.real_time_monitor()

def main():
    parser = argparse.ArgumentParser(
        description="MIDI Testing Suite - Comprehensive MIDI pipeline testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--list-devices', action='store_true',
                       help='List all available MIDI devices')
    parser.add_argument('--test-input', action='store_true',
                       help='Test MIDI input functionality')
    parser.add_argument('--test-output', action='store_true',
                       help='Test MIDI output functionality')
    parser.add_argument('--latency-test', action='store_true',
                       help='Run MIDI latency test')
    parser.add_argument('--full-diagnostic', action='store_true',
                       help='Run comprehensive pipeline diagnostics')
    parser.add_argument('--connection-test', action='store_true',
                       help='Test MIDI connections')
    parser.add_argument('--monitor', action='store_true',
                       help='Run real-time MIDI monitor')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode (default if no args)')
    
    args = parser.parse_args()
    
    suite = MIDITestSuite()
    
    # If no specific arguments provided, run interactive mode
    if not any(vars(args).values()):
        suite.run_interactive_menu()
        return
    
    if args.list_devices:
        suite.list_devices()
    
    if args.test_input:
        suite.test_input()
    
    if args.test_output:
        suite.test_output()
    
    if args.latency_test:
        suite.latency_test()
    
    if args.full_diagnostic:
        suite.full_diagnostic()
    
    if args.connection_test:
        suite.connection_test()
    
    if args.monitor:
        suite.real_time_monitor()
    
    if args.interactive:
        suite.run_interactive_menu()

if __name__ == "__main__":
    main()
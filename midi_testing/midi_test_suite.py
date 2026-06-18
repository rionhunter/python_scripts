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
from advanced_input_tester import AdvancedMIDIInputTester
from windows_midi_troubleshooter import WindowsMIDITroubleshooter
from utils import ColorPrinter, clear_screen

class MIDITestSuite:
    def __init__(self):
        self.printer = ColorPrinter()
        self.device_scanner = MIDIDeviceScanner()
        self.input_tester = MIDIInputTester()
        self.output_tester = MIDIOutputTester()
        self.latency_tester = MIDILatencyTester()
        self.diagnostics = MIDIPipelineDiagnostics()
        self.advanced_input_tester = AdvancedMIDIInputTester()
        self.troubleshooter = WindowsMIDITroubleshooter()
    
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
            print("8. Advanced Input Testing (Multi-Backend)")
            print("9. Windows MIDI Troubleshooter")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-9): ").strip()
            
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
            elif choice == '8':
                self.advanced_input_test()
            elif choice == '9':
                self.windows_troubleshoot()
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
    
    def advanced_input_test(self):
        """Advanced input testing with multiple backends."""
        clear_screen()
        self.printer.print_header("Advanced MIDI Input Testing")
        devices = self.device_scanner.get_input_devices()
        
        if not devices:
            self.printer.error("No MIDI input devices found!")
            return
        
        print("Available input devices:")
        for i, device in enumerate(devices):
            print(f"{i}: {device}")
        
        try:
            choice = int(input(f"\nSelect device for comprehensive testing (0-{len(devices)-1}): "))
            if 0 <= choice < len(devices):
                device_string = devices[choice]
                self.printer.info(f"Running comprehensive backend testing for: {device_string}")
                
                # Test with all backends
                success = self.advanced_input_tester.test_device_all_backends(device_string)
                
                if success and self.advanced_input_tester.successful_backends:
                    response = input("\nWould you like to start monitoring with a working backend? (y/n): ")
                    if response.lower() == 'y':
                        self.advanced_input_tester.test_with_working_backend(device_string)
                else:
                    self.printer.error("No backends could successfully access this device.")
                    self.printer.info("Consider running the Windows MIDI Troubleshooter (option 9)")
            else:
                self.printer.error("Invalid device selection.")
        except ValueError:
            self.printer.error("Invalid input. Please enter a number.")
    
    def windows_troubleshoot(self):
        """Run Windows MIDI troubleshooter."""
        clear_screen()
        self.printer.print_header("Windows MIDI Troubleshooter")
        
        print("Choose troubleshooting option:")
        print("1. Run full diagnosis")
        print("2. Quick fix (kill processes + restart audio service)")
        print("3. Manual fix guidance")
        print("0. Back to main menu")
        
        choice = input("\nEnter your choice (0-3): ").strip()
        
        if choice == '1':
            self.troubleshooter.run_full_diagnosis()
        elif choice == '2':
            self.printer.info("Running quick fixes...")
            self.troubleshooter._check_running_midi_processes()
            if self.troubleshooter.midi_processes:
                self.troubleshooter.kill_midi_processes()
            self.troubleshooter.restart_audio_service()
            self.printer.success("Quick fixes applied. Try your MIDI device again.")
        elif choice == '3':
            self.printer.print_header("Manual Fix Guidance")
            print("Common solutions for 'MidiInWinMM::openPort' errors:")
            print()
            print("1. Close all other MIDI applications (DAWs, music software)")
            print("2. Run this program as Administrator")
            print("3. Restart Windows Audio Service:")
            print("   - Press Win+R, type 'services.msc', press Enter")
            print("   - Find 'Windows Audio', right-click, select 'Restart'")
            print("4. Check Device Manager for MIDI device issues:")
            print("   - Press Win+X, select 'Device Manager'")
            print("   - Look for devices with yellow warning icons")
            print("5. Try a different MIDI backend (use option 8 in main menu)")
            print("6. Temporarily disable antivirus/firewall")
            print("7. Update or reinstall MIDI device drivers")
        elif choice != '0':
            self.printer.error("Invalid choice.")

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
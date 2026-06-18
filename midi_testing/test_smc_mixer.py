"""
Quick SMC-Mixer-bt MIDI Test
============================

This script specifically tests your SMC-Mixer-bt 0 device using multiple approaches
to bypass the Windows MM MIDI error you're experiencing.
"""

import sys
import time
from pathlib import Path

# Add the midi_testing directory to the path
sys.path.append(str(Path(__file__).parent))

from advanced_input_tester import AdvancedMIDIInputTester
from windows_midi_troubleshooter import WindowsMIDITroubleshooter
from utils import ColorPrinter

def main():
    printer = ColorPrinter()
    printer.print_header("SMC-Mixer-bt MIDI Device Test")
    
    # First, run troubleshooter
    printer.info("Step 1: Running Windows MIDI troubleshooter...")
    troubleshooter = WindowsMIDITroubleshooter()
    
    # Quick check for obvious issues
    troubleshooter._check_running_midi_processes()
    if troubleshooter.midi_processes:
        printer.warning(f"Found {len(troubleshooter.midi_processes)} MIDI processes running")
        response = input("Kill MIDI processes to free up device access? (y/n): ")
        if response.lower() == 'y':
            troubleshooter.kill_midi_processes()
            time.sleep(2)  # Wait for processes to fully terminate
    
    # Step 2: Test the device with all backends
    printer.info("\nStep 2: Testing SMC-Mixer-bt with all available backends...")
    tester = AdvancedMIDIInputTester()
    
    # Try to find the SMC-Mixer device
    device_string = "rtmidi:0:SMC-Mixer-bt 0"  # Based on your error message
    
    success = tester.test_device_all_backends(device_string)
    
    if success and tester.successful_backends:
        printer.success(f"\nGood news! Found working backends: {', '.join(tester.successful_backends)}")
        
        response = input("\nWould you like to start monitoring MIDI input with a working backend? (y/n): ")
        if response.lower() == 'y':
            printer.info("Starting MIDI monitoring... Press Ctrl+C to stop")
            printer.info("Try playing some notes or moving controls on your SMC-Mixer-bt")
            try:
                tester.test_with_working_backend(device_string)
            except KeyboardInterrupt:
                printer.info("Monitoring stopped.")
    else:
        printer.error("\nNo backends could access the SMC-Mixer-bt device.")
        printer.print_header("Troubleshooting Recommendations")
        
        print("The 'MidiInWinMM::openPort' error typically means:")
        print("1. Device is in use by another application")
        print("2. Windows MIDI subsystem issues")
        print("3. Driver conflicts")
        print()
        
        print("Try these solutions in order:")
        print("1. Make sure no other MIDI applications are running")
        print("2. Run this script as Administrator (right-click -> Run as administrator)")
        print("3. Restart Windows Audio Service:")
        print("   - Press Win+R, type 'services.msc', press Enter")
        print("   - Find 'Windows Audio', right-click, 'Restart'")
        print("4. Disconnect and reconnect your SMC-Mixer-bt device")
        print("5. Try a different USB port")
        print("6. Update the device drivers in Device Manager")
        
        response = input("\nWould you like to run a full system diagnosis? (y/n): ")
        if response.lower() == 'y':
            troubleshooter.run_full_diagnosis()

if __name__ == "__main__":
    main()
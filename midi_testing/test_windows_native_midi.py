"""
Test Windows Native Bluetooth MIDI
===================================

This script tests if Windows can connect to your SMC-Mixer-bt directly
without the sketchy BTMidiConnector.exe from Alibaba.
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from utils import ColorPrinter

try:
    import rtmidi
    RTMIDI_AVAILABLE = True
except ImportError:
    RTMIDI_AVAILABLE = False

def test_windows_native_midi():
    """Test Windows native Bluetooth MIDI support."""
    printer = ColorPrinter()
    printer.print_header("Windows Native Bluetooth MIDI Test")
    
    printer.info("This test will help you replace the sketchy BTMidiConnector")
    printer.info("with Windows' built-in Bluetooth MIDI support.")
    print()
    
    if not RTMIDI_AVAILABLE:
        printer.error("rtmidi not available")
        return
    
    # Step 1: Check if BTMidiConnector is still running
    import psutil
    btmidi_running = False
    for proc in psutil.process_iter(['name']):
        try:
            if 'BTMidiConnector' in proc.info['name']:
                btmidi_running = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if btmidi_running:
        printer.warning("BTMidiConnector is still running!")
        printer.info("For this test to work properly:")
        printer.info("1. Close BTMidiConnector.exe")
        printer.info("2. Disconnect SMC-Mixer-bt from BTMidiConnector")
        printer.info("3. Connect SMC-Mixer-bt via Windows Bluetooth settings")
        print()
        response = input("Have you done this? (y/n): ")
        if response.lower() != 'y':
            printer.info("Please complete those steps and run this test again.")
            return
    
    # Step 2: Scan for MIDI devices
    printer.info("Scanning for MIDI devices...")
    
    try:
        midi_in = rtmidi.MidiIn()
        input_ports = []
        
        for i in range(midi_in.get_port_count()):
            port_name = midi_in.get_port_name(i)
            input_ports.append((i, port_name))
        
        if not input_ports:
            printer.error("No MIDI input ports found!")
            printer.info("This means either:")
            printer.info("• SMC-Mixer-bt is not connected via Windows Bluetooth")
            printer.info("• Windows doesn't recognize it as a MIDI device")
            printer.info("• The device needs special drivers")
            return
        
        printer.success(f"Found {len(input_ports)} MIDI input port(s):")
        for i, name in input_ports:
            printer.print_colored(f"  {i}: {name}", 'cyan')
        
        # Step 3: Look for SMC-Mixer or similar
        smc_ports = []
        for i, name in input_ports:
            if any(keyword in name.lower() for keyword in ['smc', 'mixer', 'bt', 'bluetooth']):
                smc_ports.append((i, name))
        
        if smc_ports:
            printer.success("Found potential SMC-Mixer devices:")
            for i, name in smc_ports:
                printer.print_colored(f"  ✓ {i}: {name}", 'bright_green')
            
            # Test the first one
            test_port = smc_ports[0]
            printer.info(f"Testing port {test_port[0]}: {test_port[1]}")
            
            try:
                midi_in.open_port(test_port[0])
                printer.success("Successfully opened port!")
                
                message_count = 0
                def callback(event, data=None):
                    nonlocal message_count
                    message, deltatime = event
                    message_count += 1
                    printer.print_colored(f"MIDI: {list(message)}", 'bright_green')
                
                midi_in.set_callback(callback)
                
                printer.info("Monitoring for MIDI input...")
                printer.info("Try using your SMC-Mixer-bt controls...")
                printer.info("Press Ctrl+C to stop")
                
                try:
                    start_time = time.time()
                    while time.time() - start_time < 30:  # 30 second test
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    pass
                finally:
                    midi_in.close_port()
                    
                if message_count > 0:
                    printer.success(f"SUCCESS! Received {message_count} MIDI messages")
                    printer.success("Windows native Bluetooth MIDI is working!")
                    printer.success("You can now safely uninstall BTMidiConnector")
                    
                    printer.print_header("Next Steps")
                    print("1. Your Python MIDI applications should now work with:")
                    print(f"   Port {test_port[0]}: {test_port[1]}")
                    print("2. You can uninstall the sketchy BTMidiConnector")
                    print("3. Use this port in your MIDI applications")
                    
                else:
                    printer.warning("No MIDI messages received during test")
                    printer.info("This could mean:")
                    printer.info("• Device is connected but not sending MIDI")
                    printer.info("• Need to press buttons/move controls on device")
                    printer.info("• Device requires the original BTMidiConnector")
                    
            except Exception as e:
                printer.error(f"Failed to open port: {e}")
                printer.info("This port might not be the correct SMC-Mixer device")
                
        else:
            printer.warning("No obvious SMC-Mixer ports found")
            printer.info("Available ports might be:")
            for i, name in input_ports:
                printer.info(f"• Try testing port {i}: {name}")
        
        del midi_in
        
    except Exception as e:
        printer.error(f"Error scanning MIDI devices: {e}")

def provide_uninstall_instructions():
    """Provide instructions for removing BTMidiConnector."""
    printer = ColorPrinter()
    printer.print_header("Removing Sketchy BTMidiConnector")
    
    print("If Windows native MIDI works, you can remove BTMidiConnector:")
    print()
    print("STEP 1: Close BTMidiConnector")
    print("• End BTMidiConnector.exe process")
    print("• Check system tray for BTMidiConnector icon")
    print()
    print("STEP 2: Uninstall via Control Panel")
    print("• Windows Settings → Apps → Installed apps")
    print("• Search for 'BTMidiConnector' or 'Bt Midi Connector'")
    print("• Click three dots → Uninstall")
    print()
    print("STEP 3: Manual cleanup (if needed)")
    print("• Delete folder: C:\\Program Files (x86)\\Bt Midi Connector\\")
    print("• Check for startup entries in Task Manager")
    print()
    print("STEP 4: Connect SMC-Mixer via Windows Bluetooth")
    print("• Settings → Bluetooth & devices")
    print("• Add device → Bluetooth")
    print("• Pair SMC-Mixer-bt as standard Bluetooth device")

def main():
    """Main function."""
    print("Windows Native Bluetooth MIDI Test")
    print("==================================")
    print()
    print("This will help you replace the sketchy BTMidiConnector")
    print("with Windows' built-in Bluetooth MIDI support.")
    print()
    print("Options:")
    print("1. Test Windows native MIDI (after disconnecting BTMidiConnector)")
    print("2. Show BTMidiConnector removal instructions")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        test_windows_native_midi()
    elif choice == '2':
        provide_uninstall_instructions()
    elif choice == '3':
        print("Goodbye!")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
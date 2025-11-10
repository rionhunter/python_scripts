"""
MIDI Pipeline Diagnostics - Comprehensive system analysis for MIDI setup issues.
"""

import platform
import sys
import subprocess
import psutil
import time
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

class MIDIPipelineDiagnostics:
    """Comprehensive MIDI pipeline diagnostics and troubleshooting."""
    
    def __init__(self):
        self.printer = ColorPrinter()
        self.issues_found = []
        self.recommendations = []
    
    def run_full_diagnostic(self):
        """Run comprehensive MIDI pipeline diagnostics."""
        self.printer.print_header("MIDI Pipeline Diagnostics")
        
        self.issues_found = []
        self.recommendations = []
        
        # Run all diagnostic tests
        self._check_system_info()
        self._check_python_environment()
        self._check_midi_libraries()
        self._check_midi_devices()
        self._check_system_resources()
        self._check_audio_system()
        self._check_permissions()
        self._test_connections()
        
        # Summary
        self._show_diagnostic_summary()
    
    def _check_system_info(self):
        """Check basic system information."""
        self.printer.print_colored("System Information", 'bright_cyan')
        print("-" * 40)
        
        system_info = {
            "Operating System": f"{platform.system()} {platform.release()}",
            "Architecture": platform.machine(),
            "Python Version": sys.version.split()[0],
            "Python Path": sys.executable
        }
        
        for key, value in system_info.items():
            print(f"{key:20}: {value}")
        
        # Check for known system issues
        if platform.system() == "Windows":
            self.printer.info("Windows detected - checking for common Windows MIDI issues...")
            self._check_windows_midi_issues()
        elif platform.system() == "Darwin":
            self.printer.info("macOS detected - checking Core MIDI...")
            self._check_macos_midi_issues()
        elif platform.system() == "Linux":
            self.printer.info("Linux detected - checking ALSA/JACK...")
            self._check_linux_midi_issues()
        
        print()
    
    def _check_windows_midi_issues(self):
        """Check for Windows-specific MIDI issues."""
        # Check Windows MIDI services
        try:
            result = subprocess.run(['sc', 'query', 'Winmgmt'], 
                                  capture_output=True, text=True, timeout=10)
            if "RUNNING" in result.stdout:
                self.printer.success("Windows Management Instrumentation service is running")
            else:
                self.issues_found.append("Windows Management Instrumentation service not running")
                self.recommendations.append("Start the WMI service: sc start Winmgmt")
        except:
            self.printer.warning("Could not check Windows services")
        
        # Check for common Windows MIDI driver issues
        self.printer.info("Note: Windows built-in MIDI support should work with most devices")
        self.recommendations.append("If MIDI devices aren't detected, try updating device drivers")
    
    def _check_macos_midi_issues(self):
        """Check for macOS-specific MIDI issues."""
        try:
            # Check if Core MIDI is accessible
            result = subprocess.run(['system_profiler', 'SPAudioDataType'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.printer.success("Core MIDI system accessible")
            else:
                self.issues_found.append("Cannot access Core MIDI system")
        except:
            self.printer.warning("Could not check Core MIDI status")
        
        self.recommendations.append("Use Audio MIDI Setup.app to configure MIDI devices")
    
    def _check_linux_midi_issues(self):
        """Check for Linux-specific MIDI issues."""
        # Check ALSA
        try:
            result = subprocess.run(['aconnect', '-l'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.printer.success("ALSA MIDI system accessible")
            else:
                self.issues_found.append("ALSA MIDI system not accessible")
                self.recommendations.append("Install alsa-utils: sudo apt install alsa-utils")
        except FileNotFoundError:
            self.issues_found.append("ALSA utilities not found")
            self.recommendations.append("Install alsa-utils package")
        except:
            self.printer.warning("Could not check ALSA status")
        
        # Check for JACK
        try:
            result = subprocess.run(['jack_lsp'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.printer.success("JACK audio system detected")
            else:
                self.printer.info("JACK not running (this is okay for basic MIDI)")
        except FileNotFoundError:
            self.printer.info("JACK not installed (this is okay for basic MIDI)")
        except:
            pass
    
    def _check_python_environment(self):
        """Check Python environment and package installations."""
        self.printer.print_colored("Python Environment", 'bright_cyan')
        print("-" * 40)
        
        # Check installed packages
        packages_to_check = [
            ('rtmidi', 'python-rtmidi'),
            ('mido', 'mido'),
            ('pygame', 'pygame'),
            ('colorama', 'colorama'),
            ('psutil', 'psutil')
        ]
        
        for package_name, pip_name in packages_to_check:
            try:
                __import__(package_name)
                self.printer.success(f"{package_name} - Installed")
            except ImportError:
                self.printer.error(f"{package_name} - Not installed")
                self.issues_found.append(f"Missing package: {package_name}")
                self.recommendations.append(f"Install with: pip install {pip_name}")
        
        print()
    
    def _check_midi_libraries(self):
        """Check MIDI library functionality."""
        self.printer.print_colored("MIDI Library Tests", 'bright_cyan')
        print("-" * 40)
        
        # Test rtmidi
        if RTMIDI_AVAILABLE:
            try:
                midi_in = rtmidi.MidiIn()
                midi_out = rtmidi.MidiOut()
                input_count = midi_in.get_port_count()
                output_count = midi_out.get_port_count()
                midi_in.close_port()
                midi_out.close_port()
                del midi_in, midi_out
                
                self.printer.success(f"python-rtmidi: Found {input_count} inputs, {output_count} outputs")
            except Exception as e:
                self.printer.error(f"python-rtmidi error: {e}")
                self.issues_found.append(f"rtmidi library error: {e}")
        else:
            self.printer.warning("python-rtmidi not available")
        
        # Test mido
        if MIDO_AVAILABLE:
            try:
                input_names = mido.get_input_names()
                output_names = mido.get_output_names()
                self.printer.success(f"mido: Found {len(input_names)} inputs, {len(output_names)} outputs")
            except Exception as e:
                self.printer.error(f"mido error: {e}")
                self.issues_found.append(f"mido library error: {e}")
        else:
            self.printer.warning("mido not available")
        
        # Test pygame
        if PYGAME_AVAILABLE:
            try:
                pygame.midi.init()
                device_count = pygame.midi.get_count()
                pygame.midi.quit()
                self.printer.success(f"pygame.midi: Found {device_count} devices")
            except Exception as e:
                self.printer.error(f"pygame.midi error: {e}")
                self.issues_found.append(f"pygame.midi library error: {e}")
        else:
            self.printer.warning("pygame not available")
        
        print()
    
    def _check_midi_devices(self):
        """Check MIDI device availability and accessibility."""
        self.printer.print_colored("MIDI Device Check", 'bright_cyan')
        print("-" * 40)
        
        from device_scanner import MIDIDeviceScanner
        scanner = MIDIDeviceScanner()
        
        input_devices, output_devices = scanner.get_all_devices()
        
        if input_devices:
            self.printer.success(f"Found {len(input_devices)} input devices")
            for device in input_devices[:3]:  # Show first 3
                print(f"  • {device}")
            if len(input_devices) > 3:
                print(f"  ... and {len(input_devices) - 3} more")
        else:
            self.printer.warning("No MIDI input devices found")
            self.issues_found.append("No MIDI input devices detected")
            self.recommendations.append("Check MIDI device connections and drivers")
        
        if output_devices:
            self.printer.success(f"Found {len(output_devices)} output devices")
            for device in output_devices[:3]:  # Show first 3
                print(f"  • {device}")
            if len(output_devices) > 3:
                print(f"  ... and {len(output_devices) - 3} more")
        else:
            self.printer.warning("No MIDI output devices found")
            self.issues_found.append("No MIDI output devices detected")
            self.recommendations.append("Check MIDI device connections and drivers")
        
        print()
    
    def _check_system_resources(self):
        """Check system resources that might affect MIDI performance."""
        self.printer.print_colored("System Resources", 'bright_cyan')
        print("-" * 40)
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent < 50:
            self.printer.success(f"CPU Usage: {cpu_percent:.1f}% (Good)")
        elif cpu_percent < 80:
            self.printer.warning(f"CPU Usage: {cpu_percent:.1f}% (Moderate)")
        else:
            self.printer.error(f"CPU Usage: {cpu_percent:.1f}% (High)")
            self.issues_found.append("High CPU usage may affect MIDI timing")
            self.recommendations.append("Close unnecessary applications to reduce CPU load")
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        if memory_percent < 70:
            self.printer.success(f"Memory Usage: {memory_percent:.1f}% (Good)")
        elif memory_percent < 90:
            self.printer.warning(f"Memory Usage: {memory_percent:.1f}% (Moderate)")
        else:
            self.printer.error(f"Memory Usage: {memory_percent:.1f}% (High)")
            self.issues_found.append("High memory usage may affect system performance")
        
        # Check for audio processes that might interfere
        audio_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name'].lower()
                if any(audio_term in proc_name for audio_term in 
                      ['audio', 'sound', 'asio', 'daw', 'midi', 'music']):
                    audio_processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if audio_processes:
            self.printer.info(f"Audio-related processes found: {len(audio_processes)}")
            for proc in audio_processes[:5]:  # Show first 5
                print(f"  • {proc}")
        
        print()
    
    def _check_audio_system(self):
        """Check audio system configuration."""
        self.printer.print_colored("Audio System Check", 'bright_cyan')
        print("-" * 40)
        
        # This is a basic check - could be expanded based on OS
        if platform.system() == "Windows":
            self.printer.info("Windows audio system detected")
            self.recommendations.append("Consider ASIO drivers for low-latency audio")
        elif platform.system() == "Darwin":
            self.printer.info("Core Audio system detected")
            self.printer.success("macOS Core Audio provides good MIDI support")
        elif platform.system() == "Linux":
            self.printer.info("Linux audio system detected")
            self.recommendations.append("Consider using JACK for professional audio")
        
        print()
    
    def _check_permissions(self):
        """Check file and device permissions."""
        self.printer.print_colored("Permissions Check", 'bright_cyan')
        print("-" * 40)
        
        if platform.system() == "Linux":
            # Check if user is in audio group
            try:
                import grp
                audio_group = grp.getgrnam('audio')
                import os
                if os.getuid() in audio_group.gr_gid:
                    self.printer.success("User is in audio group")
                else:
                    self.issues_found.append("User not in audio group")
                    self.recommendations.append("Add user to audio group: sudo usermod -a -G audio $USER")
            except:
                self.printer.warning("Could not check audio group membership")
        
        # Check write permissions for temporary files
        import tempfile
        try:
            with tempfile.NamedTemporaryFile() as tmp:
                self.printer.success("Temporary file creation: OK")
        except Exception as e:
            self.issues_found.append(f"Cannot create temporary files: {e}")
        
        print()
    
    def test_connections(self):
        """Test MIDI connections."""
        self.printer.print_colored("Connection Test", 'bright_cyan')
        print("-" * 40)
        
        from device_scanner import MIDIDeviceScanner
        scanner = MIDIDeviceScanner()
        
        input_devices, output_devices = scanner.get_all_devices()
        
        if not input_devices and not output_devices:
            self.printer.error("No MIDI devices found - cannot test connections")
            return
        
        # Test device opening
        if input_devices:
            self.printer.info("Testing input device connections...")
            for i, device in enumerate(input_devices[:3]):  # Test first 3
                success = self._test_device_connection(device, 'input')
                if success:
                    self.printer.success(f"✓ {device}")
                else:
                    self.printer.error(f"✗ {device}")
                    self.issues_found.append(f"Cannot open input device: {device}")
        
        if output_devices:
            self.printer.info("Testing output device connections...")
            for i, device in enumerate(output_devices[:3]):  # Test first 3
                success = self._test_device_connection(device, 'output')
                if success:
                    self.printer.success(f"✓ {device}")
                else:
                    self.printer.error(f"✗ {device}")
                    self.issues_found.append(f"Cannot open output device: {device}")
        
        print()
    
    def _test_device_connection(self, device_string, device_type):
        """Test connection to a specific device."""
        try:
            backend, device_id, device_name = self._parse_device_string(device_string)
            
            if backend == 'mido':
                if device_type == 'input':
                    with mido.open_input(device_name):
                        pass
                else:
                    with mido.open_output(device_name):
                        pass
                return True
            elif backend == 'rtmidi':
                if device_type == 'input':
                    midi_in = rtmidi.MidiIn()
                    midi_in.open_port(device_id)
                    midi_in.close_port()
                else:
                    midi_out = rtmidi.MidiOut()
                    midi_out.open_port(device_id)
                    midi_out.close_port()
                return True
            elif backend == 'pygame':
                pygame.midi.init()
                if device_type == 'input':
                    midi_input = pygame.midi.Input(device_id)
                    midi_input.close()
                else:
                    midi_output = pygame.midi.Output(device_id)
                    midi_output.close()
                pygame.midi.quit()
                return True
                
        except Exception as e:
            return False
        
        return False
    
    def _parse_device_string(self, device_string):
        """Parse device string to extract components."""
        try:
            parts = device_string.split(':', 2)
            backend = parts[0]
            
            if backend == 'rtmidi':
                device_id = int(parts[1])
                device_name = parts[2] if len(parts) > 2 else f"Device {device_id}"
                return backend, device_id, device_name
            elif backend in ['mido', 'pygame']:
                if backend == 'pygame':
                    device_id = int(parts[1])
                    device_name = parts[2] if len(parts) > 2 else f"Device {device_id}"
                    return backend, device_id, device_name
                else:
                    device_name = ':'.join(parts[1:])
                    return backend, None, device_name
        except:
            pass
        
        return None, None, device_string
    
    def _show_diagnostic_summary(self):
        """Show diagnostic summary with issues and recommendations."""
        self.printer.print_header("Diagnostic Summary")
        
        if not self.issues_found:
            self.printer.success("✓ No major issues found!")
            self.printer.info("Your MIDI setup appears to be working correctly.")
        else:
            self.printer.error(f"Found {len(self.issues_found)} issues:")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"  {i}. {issue}")
        
        print()
        
        if self.recommendations:
            self.printer.print_colored("Recommendations:", 'bright_yellow')
            for i, rec in enumerate(self.recommendations, 1):
                print(f"  {i}. {rec}")
        
        print()
        
        # General tips
        self.printer.print_colored("General Tips:", 'bright_blue')
        tips = [
            "Ensure MIDI devices are connected before starting applications",
            "Use the latest drivers for your MIDI devices",
            "Close other MIDI applications when testing to avoid conflicts",
            "Test with simple MIDI messages first (note on/off)",
            "Check device documentation for specific setup requirements"
        ]
        
        for tip in tips:
            print(f"  • {tip}")

if __name__ == "__main__":
    diagnostics = MIDIPipelineDiagnostics()
    diagnostics.run_full_diagnostic()
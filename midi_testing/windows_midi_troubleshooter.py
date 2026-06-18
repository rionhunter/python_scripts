"""
Windows MIDI Troubleshooter - Diagnose and fix Windows-specific MIDI issues.
"""

import os
import sys
import subprocess
import winreg
import psutil
from pathlib import Path
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

class WindowsMIDITroubleshooter:
    """Comprehensive Windows MIDI troubleshooter."""
    
    def __init__(self):
        self.printer = ColorPrinter()
        self.midi_processes = []
        self.registry_issues = []
        self.driver_info = {}
    
    def run_full_diagnosis(self):
        """Run a complete MIDI system diagnosis."""
        self.printer.print_header("Windows MIDI System Diagnosis")
        
        # Check 1: MIDI Libraries
        self._check_midi_libraries()
        
        # Check 2: Running MIDI processes
        self._check_running_midi_processes()
        
        # Check 3: Windows MIDI services
        self._check_windows_midi_services()
        
        # Check 4: MIDI device drivers
        self._check_midi_device_drivers()
        
        # Check 5: Registry entries
        self._check_midi_registry()
        
        # Check 6: Permissions
        self._check_midi_permissions()
        
        # Check 7: Device conflicts
        self._check_device_conflicts()
        
        # Provide recommendations
        self._provide_recommendations()
    
    def _check_midi_libraries(self):
        """Check MIDI library installations and versions."""
        self.printer.info("Checking MIDI library installations...")
        
        libraries = {
            'python-rtmidi': RTMIDI_AVAILABLE,
            'mido': MIDO_AVAILABLE,
            'pygame': PYGAME_AVAILABLE
        }
        
        for lib, available in libraries.items():
            if available:
                try:
                    if lib == 'python-rtmidi':
                        version = rtmidi.get_rtmidi_version()
                        self.printer.success(f"{lib}: Available (v{version})")
                    elif lib == 'mido':
                        import mido
                        version = mido.__version__
                        self.printer.success(f"{lib}: Available (v{version})")
                    elif lib == 'pygame':
                        import pygame
                        version = pygame.version.ver
                        self.printer.success(f"{lib}: Available (v{version})")
                except Exception as e:
                    self.printer.warning(f"{lib}: Available but version check failed: {e}")
            else:
                self.printer.error(f"{lib}: Not available")
    
    def _check_running_midi_processes(self):
        """Check for processes that might be using MIDI devices."""
        self.printer.info("Checking for processes using MIDI resources...")
        
        midi_related_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower() if proc_info['name'] else ''
                cmdline = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
                
                # Look for MIDI-related processes
                midi_keywords = [
                    'midi', 'daw', 'cubase', 'ableton', 'reaper', 'logic', 'protools',
                    'fl studio', 'reason', 'studio one', 'nuendo', 'sonar', 'samplitude',
                    'mixcraft', 'garageband', 'audacity', 'bandlab', 'soundtrap'
                ]
                
                if any(keyword in proc_name or keyword in cmdline.lower() for keyword in midi_keywords):
                    midi_related_processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cmdline': cmdline
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if midi_related_processes:
            self.printer.warning(f"Found {len(midi_related_processes)} MIDI-related processes:")
            for proc in midi_related_processes:
                self.printer.print_colored(f"  PID {proc['pid']}: {proc['name']}", 'yellow')
            self.midi_processes = midi_related_processes
        else:
            self.printer.success("No obvious MIDI-related processes found")
    
    def _check_windows_midi_services(self):
        """Check Windows MIDI-related services."""
        self.printer.info("Checking Windows MIDI services...")
        
        services_to_check = [
            'AudioSrv',           # Windows Audio Service
            'AudioEndpointBuilder', # Windows Audio Endpoint Builder
            'Audiosrv',           # Alternative name
            'MMCSS',              # Multimedia Class Scheduler
            'Themes'              # Required for some MIDI functionality
        ]
        
        for service_name in services_to_check:
            try:
                result = subprocess.run(
                    ['sc', 'query', service_name],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                
                if result.returncode == 0:
                    if 'RUNNING' in result.stdout:
                        self.printer.success(f"Service {service_name}: Running")
                    else:
                        self.printer.warning(f"Service {service_name}: Not running")
                        # Try to get more details
                        status_lines = result.stdout.split('\n')
                        for line in status_lines:
                            if 'STATE' in line:
                                self.printer.print_colored(f"  Status: {line.strip()}", 'yellow')
                else:
                    self.printer.error(f"Service {service_name}: Not found or access denied")
                    
            except Exception as e:
                self.printer.error(f"Error checking service {service_name}: {e}")
    
    def _check_midi_device_drivers(self):
        """Check MIDI device drivers in Device Manager."""
        self.printer.info("Checking MIDI device drivers...")
        
        try:
            # Use PowerShell to get device information
            powershell_cmd = '''
            Get-WmiObject -Class Win32_PnPEntity | Where-Object {
                $_.Name -like "*midi*" -or 
                $_.Name -like "*audio*" -or
                $_.DeviceID -like "*MIDI*" -or
                $_.Service -like "*midi*"
            } | Select-Object Name, DeviceID, Status, PNPDeviceID | ConvertTo-Json
            '''
            
            result = subprocess.run(
                ['powershell', '-Command', powershell_cmd],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                import json
                try:
                    devices = json.loads(result.stdout)
                    if not isinstance(devices, list):
                        devices = [devices]
                    
                    midi_devices = []
                    for device in devices:
                        if 'midi' in device.get('Name', '').lower():
                            midi_devices.append(device)
                    
                    if midi_devices:
                        self.printer.success(f"Found {len(midi_devices)} MIDI-related devices:")
                        for device in midi_devices:
                            status = device.get('Status', 'Unknown')
                            name = device.get('Name', 'Unknown')
                            if status == 'OK':
                                self.printer.print_colored(f"  ✓ {name}: {status}", 'green')
                            else:
                                self.printer.print_colored(f"  ✗ {name}: {status}", 'red')
                    else:
                        self.printer.warning("No specific MIDI devices found in Device Manager")
                        
                except json.JSONDecodeError as e:
                    self.printer.error(f"Error parsing device information: {e}")
            else:
                self.printer.warning("Could not retrieve device information")
                
        except Exception as e:
            self.printer.error(f"Error checking device drivers: {e}")
    
    def _check_midi_registry(self):
        """Check MIDI-related registry entries."""
        self.printer.info("Checking MIDI registry entries...")
        
        registry_keys_to_check = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Drivers32"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\MediaProperties\PrivateProperties\DirectSound"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\WdmAud"),
        ]
        
        for hive, key_path in registry_keys_to_check:
            try:
                with winreg.OpenKey(hive, key_path) as key:
                    self.printer.success(f"Registry key exists: {key_path}")
                    
                    # Check for MIDI-related values
                    try:
                        i = 0
                        midi_entries = []
                        while True:
                            try:
                                name, value, reg_type = winreg.EnumValue(key, i)
                                if 'midi' in name.lower():
                                    midi_entries.append((name, value))
                                i += 1
                            except WindowsError:
                                break
                        
                        if midi_entries:
                            self.printer.print_colored(f"  Found {len(midi_entries)} MIDI entries", 'cyan')
                            for name, value in midi_entries[:3]:  # Show first 3
                                self.printer.print_colored(f"    {name}: {value}", 'white')
                        
                    except Exception as e:
                        self.printer.warning(f"  Could not enumerate values: {e}")
                        
            except FileNotFoundError:
                self.printer.warning(f"Registry key not found: {key_path}")
            except PermissionError:
                self.printer.warning(f"Permission denied accessing: {key_path}")
            except Exception as e:
                self.printer.error(f"Error checking registry key {key_path}: {e}")
    
    def _check_midi_permissions(self):
        """Check MIDI-related permissions and access rights."""
        self.printer.info("Checking MIDI permissions...")
        
        # Check if running as administrator
        try:
            is_admin = os.getuid() == 0
        except AttributeError:
            # Windows doesn't have getuid
            import ctypes
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                is_admin = False
        
        if is_admin:
            self.printer.success("Running with administrator privileges")
        else:
            self.printer.warning("Not running as administrator - this may cause MIDI access issues")
        
        # Check Windows audio service permissions
        try:
            result = subprocess.run(
                ['sc', 'sdshow', 'AudioSrv'],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0:
                self.printer.success("Audio service security descriptor accessible")
            else:
                self.printer.warning("Could not access audio service security settings")
                
        except Exception as e:
            self.printer.error(f"Error checking service permissions: {e}")
    
    def _check_device_conflicts(self):
        """Check for device conflicts that might affect MIDI."""
        self.printer.info("Checking for device conflicts...")
        
        try:
            # Use Python rtmidi to test basic device access
            if RTMIDI_AVAILABLE:
                midi_in = rtmidi.MidiIn()
                port_count = midi_in.get_port_count()
                
                self.printer.info(f"rtmidi reports {port_count} input ports available")
                
                conflicts = []
                for i in range(port_count):
                    try:
                        port_name = midi_in.get_port_name(i)
                        self.printer.print_colored(f"  Port {i}: {port_name}", 'cyan')
                        
                        # Try to open each port briefly to test for conflicts
                        try:
                            midi_in.open_port(i)
                            self.printer.print_colored(f"    ✓ Port {i} accessible", 'green')
                            midi_in.close_port()
                        except Exception as e:
                            conflicts.append((i, port_name, str(e)))
                            self.printer.print_colored(f"    ✗ Port {i} conflict: {e}", 'red')
                            
                    except Exception as e:
                        self.printer.error(f"Error testing port {i}: {e}")
                
                if conflicts:
                    self.printer.warning(f"Found {len(conflicts)} port conflicts")
                    self.device_conflicts = conflicts
                else:
                    self.printer.success("No obvious device conflicts detected")
                    
                del midi_in
            else:
                self.printer.warning("Cannot test device conflicts - rtmidi not available")
                
        except Exception as e:
            self.printer.error(f"Error checking device conflicts: {e}")
    
    def _provide_recommendations(self):
        """Provide recommendations based on the diagnosis."""
        self.printer.print_header("Troubleshooting Recommendations")
        
        recommendations = []
        
        # Check for common issues and provide solutions
        if self.midi_processes:
            recommendations.append({
                'issue': 'MIDI processes detected',
                'solution': 'Close other MIDI applications (DAWs, music software) and try again',
                'priority': 'HIGH'
            })
        
        if hasattr(self, 'device_conflicts') and self.device_conflicts:
            recommendations.append({
                'issue': 'Device access conflicts detected',
                'solution': 'Try using a different MIDI backend (mido or pygame instead of rtmidi)',
                'priority': 'HIGH'
            })
        
        # Always include general Windows MIDI fixes
        recommendations.extend([
            {
                'issue': 'Windows MM MIDI driver issues',
                'solution': 'Restart Windows Audio Service: Run "services.msc", find "Windows Audio", restart it',
                'priority': 'MEDIUM'
            },
            {
                'issue': 'MIDI driver conflicts',
                'solution': 'Update/reinstall MIDI device drivers in Device Manager',
                'priority': 'MEDIUM'
            },
            {
                'issue': 'Permission issues',
                'solution': 'Run Python script as Administrator',
                'priority': 'MEDIUM'
            },
            {
                'issue': 'ASIO driver conflicts',
                'solution': 'Temporarily disable ASIO drivers if present (ASIO4ALL, etc.)',
                'priority': 'LOW'
            },
            {
                'issue': 'Windows exclusive mode',
                'solution': 'Disable exclusive mode in Windows Sound settings for MIDI devices',
                'priority': 'LOW'
            }
        ])
        
        # Sort by priority
        priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        recommendations.sort(key=lambda x: priority_order[x['priority']])
        
        for i, rec in enumerate(recommendations, 1):
            priority_color = {'HIGH': 'red', 'MEDIUM': 'yellow', 'LOW': 'cyan'}[rec['priority']]
            self.printer.print_colored(f"{i}. [{rec['priority']}] {rec['issue']}", priority_color)
            self.printer.print_colored(f"   Solution: {rec['solution']}", 'white')
            print()
    
    def restart_audio_service(self):
        """Restart Windows Audio Service."""
        self.printer.info("Attempting to restart Windows Audio Service...")
        
        try:
            # Stop the service
            result1 = subprocess.run(['net', 'stop', 'AudioSrv'], 
                                   capture_output=True, text=True, shell=True)
            
            if result1.returncode == 0:
                self.printer.success("Audio service stopped")
                
                # Start the service
                result2 = subprocess.run(['net', 'start', 'AudioSrv'], 
                                       capture_output=True, text=True, shell=True)
                
                if result2.returncode == 0:
                    self.printer.success("Audio service restarted successfully")
                    return True
                else:
                    self.printer.error(f"Failed to start audio service: {result2.stderr}")
            else:
                self.printer.error(f"Failed to stop audio service: {result1.stderr}")
                
        except Exception as e:
            self.printer.error(f"Error restarting audio service: {e}")
        
        return False
    
    def kill_midi_processes(self):
        """Kill detected MIDI processes."""
        if not self.midi_processes:
            self.printer.info("No MIDI processes to kill")
            return True
        
        self.printer.warning(f"Attempting to terminate {len(self.midi_processes)} MIDI processes...")
        
        killed_count = 0
        for proc_info in self.midi_processes:
            try:
                proc = psutil.Process(proc_info['pid'])
                proc.terminate()
                
                # Wait for termination
                try:
                    proc.wait(timeout=5)
                    self.printer.success(f"Terminated: {proc_info['name']} (PID {proc_info['pid']})")
                    killed_count += 1
                except psutil.TimeoutExpired:
                    # Force kill if terminate doesn't work
                    proc.kill()
                    self.printer.warning(f"Force killed: {proc_info['name']} (PID {proc_info['pid']})")
                    killed_count += 1
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.printer.error(f"Could not terminate {proc_info['name']}: {e}")
        
        if killed_count > 0:
            self.printer.success(f"Successfully terminated {killed_count} processes")
            return True
        else:
            self.printer.error("Could not terminate any processes")
            return False

def main():
    """Main function for the troubleshooter."""
    troubleshooter = WindowsMIDITroubleshooter()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        # Attempt automatic fixes
        troubleshooter.printer.print_header("Windows MIDI Auto-Fix")
        
        # Kill MIDI processes
        troubleshooter._check_running_midi_processes()
        if troubleshooter.midi_processes:
            response = input("Kill MIDI processes? (y/n): ")
            if response.lower() == 'y':
                troubleshooter.kill_midi_processes()
        
        # Restart audio service
        response = input("Restart Windows Audio Service? (y/n): ")
        if response.lower() == 'y':
            troubleshooter.restart_audio_service()
        
        print("\nTry your MIDI application again.")
    else:
        # Run full diagnosis
        troubleshooter.run_full_diagnosis()

if __name__ == "__main__":
    main()
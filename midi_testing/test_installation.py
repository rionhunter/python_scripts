"""
Test runner to verify MIDI Testing Suite installation and basic functionality.
"""

import sys
from pathlib import Path

# Add the midi_testing directory to the path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from device_scanner import MIDIDeviceScanner
        print("✓ device_scanner imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import device_scanner: {e}")
        return False
    
    try:
        from input_tester import MIDIInputTester
        print("✓ input_tester imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import input_tester: {e}")
        return False
    
    try:
        from output_tester import MIDIOutputTester
        print("✓ output_tester imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import output_tester: {e}")
        return False
    
    try:
        from latency_tester import MIDILatencyTester
        print("✓ latency_tester imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import latency_tester: {e}")
        return False
    
    try:
        from pipeline_diagnostics import MIDIPipelineDiagnostics
        print("✓ pipeline_diagnostics imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pipeline_diagnostics: {e}")
        return False
    
    try:
        from utils import ColorPrinter
        print("✓ utils imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import utils: {e}")
        return False
    
    return True

def test_dependencies():
    """Test that required dependencies are available."""
    print("\nTesting dependencies...")
    
    dependencies = [
        ('colorama', 'colorama'),
        ('psutil', 'psutil'),
    ]
    
    optional_dependencies = [
        ('rtmidi', 'python-rtmidi'),
        ('mido', 'mido'),
        ('pygame', 'pygame'),
    ]
    
    all_good = True
    
    # Test required dependencies
    for module_name, pip_name in dependencies:
        try:
            __import__(module_name)
            print(f"✓ {module_name} available")
        except ImportError:
            print(f"✗ {module_name} not available - install with: pip install {pip_name}")
            all_good = False
    
    # Test optional dependencies (at least one MIDI library should be available)
    midi_available = False
    for module_name, pip_name in optional_dependencies:
        try:
            __import__(module_name)
            print(f"✓ {module_name} available")
            if module_name in ['rtmidi', 'mido', 'pygame']:
                midi_available = True
        except ImportError:
            print(f"○ {module_name} not available (optional) - install with: pip install {pip_name}")
    
    if not midi_available:
        print("✗ No MIDI libraries available! Install at least one: python-rtmidi, mido, or pygame")
        all_good = False
    
    return all_good

def test_basic_functionality():
    """Test basic functionality without requiring MIDI devices."""
    print("\nTesting basic functionality...")
    
    try:
        from device_scanner import MIDIDeviceScanner
        from utils import ColorPrinter
        
        # Test ColorPrinter
        printer = ColorPrinter()
        printer.success("ColorPrinter working")
        
        # Test device scanner (should work even without devices)
        scanner = MIDIDeviceScanner()
        scanner.check_backend_availability()
        
        # Try to get devices (might be empty, but shouldn't crash)
        input_devices, output_devices = scanner.get_all_devices()
        print(f"✓ Device scanning works - found {len(input_devices)} inputs, {len(output_devices)} outputs")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("MIDI Testing Suite - Installation Test")
    print("=" * 50)
    
    # Run tests
    imports_ok = test_imports()
    deps_ok = test_dependencies()
    basic_ok = test_basic_functionality()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"Imports:      {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"Dependencies: {'✓ PASS' if deps_ok else '✗ FAIL'}")
    print(f"Basic Tests:  {'✓ PASS' if basic_ok else '✗ FAIL'}")
    
    if imports_ok and deps_ok and basic_ok:
        print("\n🎉 All tests passed! The MIDI Testing Suite is ready to use.")
        print("Run 'python midi_test_suite.py' to start the interactive suite.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("You may need to install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    return imports_ok and deps_ok and basic_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
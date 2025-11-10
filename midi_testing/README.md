# MIDI Testing Suite

A comprehensive MIDI testing and diagnostics toolkit for identifying issues in MIDI pipelines. This suite helps developers and musicians troubleshoot MIDI connectivity, latency, and functionality problems.

## Features

### 🔍 Device Detection
- Scans for available MIDI input/output devices
- Supports multiple backends (python-rtmidi, mido, pygame)
- Cross-platform compatibility (Windows, macOS, Linux)

### 📥 Input Testing
- Real-time MIDI message monitoring
- Formatted display of note events, control changes, program changes
- Visual velocity bars and note name conversion
- Active note tracking

### 📤 Output Testing
- Comprehensive test suite for MIDI output devices
- Tests include: basic notes, velocity sensitivity, channel testing
- Control change, program change, and pitch bend testing
- Interactive note player

### ⏱️ Latency Testing
- Round-trip latency measurement
- Statistical analysis (min, max, average, median, standard deviation)
- Jitter analysis and performance assessment
- Latency distribution histogram

### 🔧 Pipeline Diagnostics
- System information and compatibility checks
- MIDI library functionality testing
- Resource usage monitoring
- Permission and configuration verification
- OS-specific troubleshooting

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Required packages:
- `python-rtmidi>=1.4.9` - Low-level MIDI I/O
- `mido>=1.2.10` - High-level MIDI library
- `pygame>=2.1.0` - Alternative MIDI backend
- `colorama>=0.4.4` - Cross-platform colored terminal output
- `psutil>=5.9.0` - System monitoring

## Usage

### Command Line Interface

```bash
# Interactive mode (default)
python midi_test_suite.py

# List all MIDI devices
python midi_test_suite.py --list-devices

# Test MIDI input
python midi_test_suite.py --test-input

# Test MIDI output
python midi_test_suite.py --test-output

# Run latency test
python midi_test_suite.py --latency-test

# Full diagnostic
python midi_test_suite.py --full-diagnostic

# Real-time MIDI monitor
python midi_test_suite.py --monitor
```

### Interactive Menu

The interactive mode provides an easy-to-use menu system:

```
MIDI Testing Suite - Interactive Mode
=====================================

Select a test to run:
1. List MIDI Devices
2. Test MIDI Input
3. Test MIDI Output
4. Latency Test
5. Full Pipeline Diagnostics
6. Connection Test
7. Real-time Monitor
0. Exit
```

### Individual Components

You can also run individual components directly:

```bash
# Device scanner
python device_scanner.py

# Input tester
python input_tester.py

# Output tester
python output_tester.py

# Latency tester
python latency_tester.py

# Pipeline diagnostics
python pipeline_diagnostics.py
```

## Use Cases

### 🎹 For Musicians
- Verify MIDI keyboard/controller connectivity
- Test MIDI software/hardware compatibility
- Measure latency for live performance setup
- Troubleshoot MIDI routing issues

### 👨‍💻 For Developers
- Debug MIDI application integration
- Identify pipeline bottlenecks
- Test MIDI library compatibility
- Validate MIDI message handling

### 🔧 For System Administrators
- Diagnose MIDI driver issues
- Verify system MIDI configuration
- Monitor MIDI device performance
- Troubleshoot permission problems

## Test Types

### Basic Device Tests
- Device enumeration and availability
- Device connection and access testing
- Backend compatibility verification

### Functional Tests
- MIDI message transmission/reception
- Message type handling (notes, CC, program change, etc.)
- Channel and velocity testing
- Timing accuracy verification

### Performance Tests
- Round-trip latency measurement
- Jitter analysis
- Resource usage monitoring
- Throughput testing

### Diagnostic Tests
- System configuration analysis
- Driver and service verification
- Permission and access checking
- Environment compatibility testing

## Troubleshooting Guide

### Common Issues

**No MIDI devices found:**
- Check device connections and power
- Verify device drivers are installed
- Ensure device is not in use by another application
- Check system MIDI settings

**High latency:**
- Close unnecessary applications
- Use ASIO drivers on Windows
- Check audio buffer settings
- Consider using dedicated MIDI interface

**Permission errors (Linux):**
- Add user to audio group: `sudo usermod -a -G audio $USER`
- Check device file permissions
- Verify ALSA configuration

**Library import errors:**
- Install missing dependencies: `pip install -r requirements.txt`
- Check Python environment and paths
- Verify package versions

### Platform-Specific Notes

**Windows:**
- Built-in Windows MIDI support should work for most devices
- Consider ASIO drivers for professional audio interfaces
- Check Windows Audio service is running

**macOS:**
- Uses Core MIDI framework
- Configure devices in Audio MIDI Setup app
- Most USB MIDI devices work automatically

**Linux:**
- Requires ALSA for basic MIDI support
- Consider JACK for professional audio
- Install `alsa-utils` package for MIDI utilities

## API Reference

### MIDIDeviceScanner
```python
scanner = MIDIDeviceScanner()
input_devices, output_devices = scanner.get_all_devices()
scanner.scan_and_display_devices()
```

### MIDIInputTester
```python
tester = MIDIInputTester()
tester.test_device("mido:Your MIDI Device")
tester.real_time_monitor()
```

### MIDIOutputTester
```python
tester = MIDIOutputTester()
tester.test_device("mido:Your MIDI Device")
```

### MIDILatencyTester
```python
tester = MIDILatencyTester()
tester.run_latency_test()
```

### MIDIPipelineDiagnostics
```python
diagnostics = MIDIPipelineDiagnostics()
diagnostics.run_full_diagnostic()
```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Support

For support and questions, please open an issue on the project repository.
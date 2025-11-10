# Motorized Fader & LED Testing Features

## New Test Options Added

The MIDI output tester now includes advanced testing capabilities for modern MIDI controllers with motorized faders and LED feedback:

### 7. Motorized Fader Test (all channels)
- **Purpose**: Tests motorized fader movement by sending position feedback
- **Coverage**: All 16 MIDI channels
- **CC Numbers Tested**: 
  - CC 0 (Bank Select MSB)
  - CC 1 (Modulation Wheel)
  - CC 7 (Volume - most common for faders)
  - CC 10 (Pan)
  - CC 11 (Expression)
  - CC 14-21 (General purpose controllers)
- **Pattern**: Sweeps fader positions from 0 → 32 → 64 → 96 → 127 → 96 → 64 → 32 → 0
- **Reset**: All faders return to center position (64) at the end

### 8. Light/LED Test (all channels)
- **Purpose**: Tests LED/light feedback on buttons, pads, and indicators
- **Test Types**:
  - **Note-based LEDs**: Tests drum pad range (notes 36-83) with note on/off
  - **CC-based LEDs**: Tests button controllers (CC 64-79) with 0/127 values
  - **Program LEDs**: Tests program change buttons (programs 0-15)
  - **RGB LED Test**: Tests color LEDs with various velocities (Novation/AKAI style)
- **Coverage**: All 16 MIDI channels
- **Color Test**: Simulates RGB colors (Red, Green, Blue, Yellow, Magenta, Cyan, White)

### 9. Advanced Controller Test (faders + lights)
- **Purpose**: Simulates real-world mixing console scenarios
- **Features**:
  - **Mixing Console Simulation**: 8-channel fader automation with LED feedback
  - **Master Section**: Master fader with LED level meters
  - **Transport Control**: Play, Stop, Record, Rewind, Fast Forward buttons
  - **Synchronized Control**: Fader positions control corresponding LED brightness
- **Reset**: All controls return to off/zero state at the end

### 10. Comprehensive Test (updated)
Now includes all tests in sequence:
1. Basic Notes
2. Velocity Test
3. Channel Test
4. Control Change Test
5. Program Change Test
6. Pitch Bend Test
7. **Motorized Faders** (NEW)
8. **Light/LED Feedback** (NEW)
9. **Advanced Controller** (NEW)

## Supported Controller Types

### Motorized Fader Controllers
- Behringer X-Touch series
- Mackie Control Universal
- Avid Artist Mix/Control
- SSL Nucleus series
- PreSonus FaderPort series
- Icon Platform series

### LED Controllers
- Novation Launchpad series
- AKAI APC series
- Ableton Push series
- Native Instruments Maschine
- Arturia BeatStep series
- Keith McMillen QuNeo

### Advanced Controllers (Faders + LEDs)
- Behringer X-Touch (motorized faders + LEDs)
- SSL UF8 (motorized faders + LEDs)
- Avid S1/S3/S6 series
- Solid State Logic SiX series
- PreSonus FaderPort 16

## How It Works

### Motorized Fader Testing
1. Sends Control Change messages on common fader CC numbers
2. Sweeps through position values to trigger fader movement
3. Tests multiple CC numbers as different controllers map faders differently
4. Resets all faders to center position for consistency

### LED Testing
1. **Note-based**: Sends Note On (127 velocity) and Note Off (0 velocity)
2. **CC-based**: Sends Control Change with values 127 (on) and 0 (off)
3. **RGB testing**: Uses velocity values to simulate color intensity
4. Tests multiple protocols as LED implementations vary by manufacturer

### Advanced Controller Testing
1. **Fader Automation**: Simulates DAW automation with smooth fader sweeps
2. **LED Feedback**: Brightness corresponds to fader position
3. **Transport Control**: Tests standard DAW transport button LEDs
4. **Master Section**: Multi-LED level meter simulation

## Usage Tips

- **Connect your MIDI controller** before running tests
- **Check your controller's MIDI implementation** - different manufacturers use different CC numbers
- **Watch for visual feedback** - motorized faders should move, LEDs should light up
- **Use with loopback testing** - connect MIDI out to MIDI in to verify signal flow
- **Test systematically** - start with individual tests before running comprehensive test

## Troubleshooting

### Motorized Faders Not Moving
- Check if controller supports motorized fader feedback
- Verify CC numbers match your controller's MIDI implementation
- Ensure controller is in the correct MIDI mode
- Check power supply to controller (motorized faders require power)

### LEDs Not Lighting
- Verify controller supports LED feedback
- Check note numbers and CC assignments
- Some controllers require specific protocols (e.g., SysEx)
- Ensure controller is not in local off mode

### Partial Response
- Different controllers respond to different MIDI messages
- Check your controller's manual for MIDI implementation chart
- Some features may require specific firmware versions
- Try different test patterns to find what works with your controller

This enhanced testing capability makes the MIDI Testing Suite ideal for validating advanced MIDI controller setups and diagnosing feedback issues in professional audio environments.
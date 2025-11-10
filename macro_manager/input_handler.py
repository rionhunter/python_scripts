"""
Input Handler - Multi-device input system for macro triggers
Supports: Secondary keyboards, game controllers, MIDI devices, text commands, AI dictation
"""

import threading
from queue import Queue
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class InputDeviceType(Enum):
    KEYBOARD = "keyboard"
    GAME_CONTROLLER = "game_controller"
    MIDI = "midi"
    TEXT_COMMAND = "text_command"
    AI_DICTATION = "ai_dictation"


@dataclass
class InputEvent:
    """Represents an input event from any device"""
    device_type: InputDeviceType
    device_id: str
    event_type: str  # press, release, value_change, command
    data: Dict[str, Any]
    timestamp: float


class InputDevice:
    """Base class for input devices"""
    
    def __init__(self, device_id: str, device_type: InputDeviceType):
        self.device_id = device_id
        self.device_type = device_type
        self.enabled = True
        self.callbacks = []
        
    def register_callback(self, callback: Callable[[InputEvent], None]):
        """Register a callback to be called when input is received"""
        self.callbacks.append(callback)
        
    def emit_event(self, event: InputEvent):
        """Emit an event to all registered callbacks"""
        if self.enabled:
            for callback in self.callbacks:
                callback(event)
    
    def start(self):
        """Start listening for input"""
        raise NotImplementedError
    
    def stop(self):
        """Stop listening for input"""
        raise NotImplementedError


class KeyboardDevice(InputDevice):
    """Handles secondary keyboard input"""
    
    def __init__(self, device_id: str):
        super().__init__(device_id, InputDeviceType.KEYBOARD)
        self.listening = False
        self.thread = None
        
    def start(self):
        """Start listening for keyboard input"""
        if self.listening:
            return
            
        self.listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop listening for keyboard input"""
        self.listening = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _listen_loop(self):
        """Main listening loop - requires keyboard library"""
        try:
            import keyboard
            import time
            
            def on_key_event(event):
                if not self.listening:
                    return
                    
                input_event = InputEvent(
                    device_type=self.device_type,
                    device_id=self.device_id,
                    event_type="press" if event.event_type == "down" else "release",
                    data={
                        "key": event.name,
                        "scan_code": event.scan_code,
                        "is_keypad": event.is_keypad
                    },
                    timestamp=time.time()
                )
                self.emit_event(input_event)
            
            keyboard.hook(on_key_event)
            
            while self.listening:
                time.sleep(0.1)
                
            keyboard.unhook_all()
            
        except ImportError:
            print("keyboard library not installed. Install with: pip install keyboard")
        except Exception as e:
            print(f"Error in keyboard listener: {e}")


class GameControllerDevice(InputDevice):
    """Handles game controller input"""
    
    def __init__(self, device_id: str, controller_index: int = 0):
        super().__init__(device_id, InputDeviceType.GAME_CONTROLLER)
        self.controller_index = controller_index
        self.listening = False
        self.thread = None
        
    def start(self):
        """Start listening for controller input"""
        if self.listening:
            return
            
        self.listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop listening for controller input"""
        self.listening = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _listen_loop(self):
        """Main listening loop - requires pygame"""
        try:
            import pygame
            import time
            
            pygame.init()
            pygame.joystick.init()
            
            if pygame.joystick.get_count() <= self.controller_index:
                print(f"Controller {self.controller_index} not found")
                return
            
            joystick = pygame.joystick.Joystick(self.controller_index)
            joystick.init()
            
            print(f"Controller connected: {joystick.get_name()}")
            
            while self.listening:
                pygame.event.pump()
                
                # Check buttons
                for i in range(joystick.get_numbuttons()):
                    button_state = joystick.get_button(i)
                    # You'd want to track previous state to detect changes
                    
                # Check axes
                for i in range(joystick.get_numaxes()):
                    axis_value = joystick.get_axis(i)
                    # Process axis changes
                    
                # Check hats (D-pad)
                for i in range(joystick.get_numhats()):
                    hat_value = joystick.get_hat(i)
                    # Process hat changes
                
                time.sleep(0.016)  # ~60Hz polling
                
            pygame.quit()
            
        except ImportError:
            print("pygame library not installed. Install with: pip install pygame")
        except Exception as e:
            print(f"Error in controller listener: {e}")


class MIDIDevice(InputDevice):
    """Handles MIDI device input"""
    
    def __init__(self, device_id: str, midi_port: Optional[str] = None):
        super().__init__(device_id, InputDeviceType.MIDI)
        self.midi_port = midi_port
        self.listening = False
        self.thread = None
        
    def start(self):
        """Start listening for MIDI input"""
        if self.listening:
            return
            
        self.listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop listening for MIDI input"""
        self.listening = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _listen_loop(self):
        """Main listening loop - requires mido"""
        try:
            import mido
            import time
            
            # List available ports
            available_ports = mido.get_input_names()
            print(f"Available MIDI ports: {available_ports}")
            
            if not available_ports:
                print("No MIDI devices found")
                return
            
            # Use specified port or first available
            port_name = self.midi_port if self.midi_port in available_ports else available_ports[0]
            
            with mido.open_input(port_name) as inport:
                print(f"MIDI listening on: {port_name}")
                
                for msg in inport:
                    if not self.listening:
                        break
                    
                    input_event = InputEvent(
                        device_type=self.device_type,
                        device_id=self.device_id,
                        event_type="midi_message",
                        data={
                            "type": msg.type,
                            "note": getattr(msg, 'note', None),
                            "velocity": getattr(msg, 'velocity', None),
                            "control": getattr(msg, 'control', None),
                            "value": getattr(msg, 'value', None),
                            "channel": getattr(msg, 'channel', None)
                        },
                        timestamp=time.time()
                    )
                    self.emit_event(input_event)
                    
        except ImportError:
            print("mido library not installed. Install with: pip install mido python-rtmidi")
        except Exception as e:
            print(f"Error in MIDI listener: {e}")


class TextCommandDevice(InputDevice):
    """Handles text command input"""
    
    def __init__(self, device_id: str):
        super().__init__(device_id, InputDeviceType.TEXT_COMMAND)
        self.command_queue = Queue()
        
    def submit_command(self, command_text: str):
        """Submit a text command for processing"""
        import time
        
        input_event = InputEvent(
            device_type=self.device_type,
            device_id=self.device_id,
            event_type="command",
            data={"command": command_text},
            timestamp=time.time()
        )
        self.emit_event(input_event)
    
    def start(self):
        """Text commands don't need continuous listening"""
        pass
    
    def stop(self):
        """Text commands don't need cleanup"""
        pass


class AIDictationDevice(InputDevice):
    """Handles AI-powered voice dictation and conversation"""
    
    def __init__(self, device_id: str):
        super().__init__(device_id, InputDeviceType.AI_DICTATION)
        self.listening = False
        self.thread = None
        self.recognizer = None
        
    def start(self):
        """Start listening for voice input"""
        if self.listening:
            return
            
        self.listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop listening for voice input"""
        self.listening = False
        if self.thread:
            self.thread.join(timeout=1.0)
    
    def _listen_loop(self):
        """Main listening loop - requires speech_recognition"""
        try:
            import speech_recognition as sr
            import time
            
            self.recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                print("AI Dictation: Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("AI Dictation: Ready")
                
                while self.listening:
                    try:
                        print("AI Dictation: Listening...")
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        
                        # Try to recognize speech
                        try:
                            text = self.recognizer.recognize_google(audio)
                            print(f"Recognized: {text}")
                            
                            input_event = InputEvent(
                                device_type=self.device_type,
                                device_id=self.device_id,
                                event_type="dictation",
                                data={"text": text, "confidence": 1.0},
                                timestamp=time.time()
                            )
                            self.emit_event(input_event)
                            
                        except sr.UnknownValueError:
                            print("Could not understand audio")
                        except sr.RequestError as e:
                            print(f"Recognition service error: {e}")
                            
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        print(f"Error in dictation: {e}")
                        time.sleep(1)
                        
        except ImportError:
            print("speech_recognition library not installed. Install with: pip install SpeechRecognition pyaudio")
        except Exception as e:
            print(f"Error initializing dictation: {e}")


class InputManager:
    """Manages all input devices and routes events"""
    
    def __init__(self):
        self.devices: Dict[str, InputDevice] = {}
        self.event_handlers = []
        
    def add_device(self, device: InputDevice):
        """Add an input device"""
        self.devices[device.device_id] = device
        device.register_callback(self._on_device_event)
        
    def remove_device(self, device_id: str):
        """Remove an input device"""
        if device_id in self.devices:
            self.devices[device_id].stop()
            del self.devices[device_id]
    
    def start_all(self):
        """Start all devices"""
        for device in self.devices.values():
            device.start()
    
    def stop_all(self):
        """Stop all devices"""
        for device in self.devices.values():
            device.stop()
    
    def register_event_handler(self, handler: Callable[[InputEvent], None]):
        """Register a handler for all input events"""
        self.event_handlers.append(handler)
    
    def _on_device_event(self, event: InputEvent):
        """Internal event handler that routes to all registered handlers"""
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler: {e}")
    
    def get_device(self, device_id: str) -> Optional[InputDevice]:
        """Get a device by ID"""
        return self.devices.get(device_id)
    
    def list_devices(self) -> list:
        """List all registered devices"""
        return [
            {
                "id": device.device_id,
                "type": device.device_type.value,
                "enabled": device.enabled
            }
            for device in self.devices.values()
        ]


# Example usage
if __name__ == "__main__":
    import time
    
    def handle_event(event: InputEvent):
        print(f"Event from {event.device_type.value}: {event.event_type} - {event.data}")
    
    manager = InputManager()
    manager.register_event_handler(handle_event)
    
    # Add devices
    keyboard_device = KeyboardDevice("main_keyboard")
    manager.add_device(keyboard_device)
    
    text_command = TextCommandDevice("text_commands")
    manager.add_device(text_command)
    
    # Start listening
    manager.start_all()
    
    # Simulate text command
    time.sleep(1)
    text_command.submit_command("open notepad")
    
    try:
        print("Press Ctrl+C to exit...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        manager.stop_all()

"""
Utility functions for the MIDI testing suite.
"""

import os
import sys
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows compatibility
init()

class ColorPrinter:
    """Utility class for colored console output."""
    
    def __init__(self):
        self.colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE,
            'bright_red': Fore.LIGHTRED_EX,
            'bright_green': Fore.LIGHTGREEN_EX,
            'bright_yellow': Fore.LIGHTYELLOW_EX,
            'bright_blue': Fore.LIGHTBLUE_EX,
            'bright_magenta': Fore.LIGHTMAGENTA_EX,
            'bright_cyan': Fore.LIGHTCYAN_EX,
        }
    
    def print_header(self, text):
        """Print a styled header."""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{text.center(60)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    def success(self, text):
        """Print success message in green."""
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")
    
    def error(self, text):
        """Print error message in red."""
        print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")
    
    def warning(self, text):
        """Print warning message in yellow."""
        print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")
    
    def info(self, text):
        """Print info message in blue."""
        print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")
    
    def print_colored(self, text, color='white'):
        """Print text in specified color."""
        color_code = self.colors.get(color, Fore.WHITE)
        print(f"{color_code}{text}{Style.RESET_ALL}")
    
    def print_midi_message(self, msg_type, channel, data1, data2=None):
        """Print formatted MIDI message."""
        if data2 is not None:
            print(f"{Fore.CYAN}MIDI: {Fore.YELLOW}{msg_type} {Fore.GREEN}Ch:{channel} "
                  f"{Fore.MAGENTA}Data1:{data1} Data2:{data2}{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}MIDI: {Fore.YELLOW}{msg_type} {Fore.GREEN}Ch:{channel} "
                  f"{Fore.MAGENTA}Data:{data1}{Style.RESET_ALL}")

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_midi_message(message):
    """Format a MIDI message for display."""
    if hasattr(message, 'type'):
        # mido message
        if message.type == 'note_on':
            return f"Note On - Ch:{message.channel} Note:{message.note} Vel:{message.velocity}"
        elif message.type == 'note_off':
            return f"Note Off - Ch:{message.channel} Note:{message.note} Vel:{message.velocity}"
        elif message.type == 'control_change':
            return f"CC - Ch:{message.channel} Control:{message.control} Value:{message.value}"
        elif message.type == 'program_change':
            return f"Program Change - Ch:{message.channel} Program:{message.program}"
        elif message.type == 'pitchwheel':
            return f"Pitch Bend - Ch:{message.channel} Value:{message.pitch}"
        else:
            return f"{message.type} - {message}"
    else:
        # Raw MIDI data
        return f"Raw MIDI: {message}"

def note_number_to_name(note_number):
    """Convert MIDI note number to note name."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (note_number // 12) - 1
    note = notes[note_number % 12]
    return f"{note}{octave}"

def velocity_to_bar(velocity, width=20):
    """Convert MIDI velocity to a visual bar."""
    filled = int((velocity / 127) * width)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {velocity:3d}"

def format_time(seconds):
    """Format time in seconds to a readable string."""
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"

class ProgressBar:
    """Simple progress bar for console."""
    
    def __init__(self, total, width=50, prefix='Progress'):
        self.total = total
        self.width = width
        self.prefix = prefix
        self.current = 0
    
    def update(self, current):
        """Update progress bar."""
        self.current = current
        percent = (current / self.total) * 100
        filled = int((current / self.total) * self.width)
        bar = '█' * filled + '░' * (self.width - filled)
        
        print(f'\r{self.prefix}: [{bar}] {percent:.1f}% ({current}/{self.total})',
              end='', flush=True)
        
        if current >= self.total:
            print()  # New line when complete

def get_user_choice(prompt, choices):
    """Get user choice from a list of options."""
    while True:
        try:
            print(f"\n{prompt}")
            for i, choice in enumerate(choices):
                print(f"{i}: {choice}")
            
            selection = int(input(f"Enter choice (0-{len(choices)-1}): "))
            if 0 <= selection < len(choices):
                return selection, choices[selection]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None, None
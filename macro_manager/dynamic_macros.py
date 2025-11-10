"""
Dynamic Macro System - Parse and execute macros with runtime variables
Examples: "delete last 3 words", "repeat 5 times", "wait 200 milliseconds"
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ParsedVariable:
    """Represents a parsed variable from user input"""
    name: str
    value: Any
    type: str  # 'number', 'text', 'duration'


class DynamicMacroParser:
    """Parse natural language commands and extract variables"""
    
    # Common patterns for extracting variables
    PATTERNS = {
        'number': [
            r'(\d+)',  # Any number
            r'(one|two|three|four|five|six|seven|eight|nine|ten)',  # Written numbers
        ],
        'duration': [
            r'(\d+)\s*(?:ms|milliseconds?)',
            r'(\d+)\s*(?:s|seconds?)',
            r'(\d+)\s*(?:m|minutes?)',
        ],
        'direction': [
            r'(up|down|left|right|forward|back)',
        ],
        'position': [
            r'(first|last|next|previous)',
        ]
    }
    
    # Number word to digit conversion
    WORD_TO_NUMBER = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
        'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
        'nineteen': 19, 'twenty': 20
    }
    
    def __init__(self):
        self.command_templates = {
            'delete_words': [
                r'delete\s+(?:the\s+)?last\s+(\d+)\s+words?',
                r'remove\s+(?:the\s+)?last\s+(\d+)\s+words?',
                r'delete\s+(\d+)\s+words?',
            ],
            'repeat': [
                r'repeat\s+(\d+)\s+times?',
                r'do\s+(\d+)\s+times?',
            ],
            'wait': [
                r'wait\s+(\d+)\s*(?:ms|milliseconds?)',
                r'wait\s+(\d+)\s*(?:s|seconds?)',
                r'pause\s+(?:for\s+)?(\d+)\s*(?:ms|milliseconds?)',
            ],
            'type_text': [
                r'type\s+["\'](.+?)["\']',
                r'write\s+["\'](.+?)["\']',
            ],
            'press_key': [
                r'press\s+(\w+)',
                r'hit\s+(\w+)',
            ],
            'click': [
                r'click\s+(?:at\s+)?(\d+),\s*(\d+)',
                r'click\s+(left|right|middle)',
            ],
            'open': [
                r'open\s+(.+)',
                r'launch\s+(.+)',
            ],
        }
    
    def parse_command(self, command: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Parse a natural language command and extract variables
        Returns: (command_type, variables_dict)
        """
        command = command.lower().strip()
        
        for cmd_type, patterns in self.command_templates.items():
            for pattern in patterns:
                match = re.search(pattern, command)
                if match:
                    variables = self._extract_variables(cmd_type, match)
                    return cmd_type, variables
        
        return None, {}
    
    def _extract_variables(self, cmd_type: str, match) -> Dict[str, Any]:
        """Extract variables from regex match based on command type"""
        variables = {}
        
        if cmd_type == 'delete_words':
            count = int(match.group(1))
            variables = {'count': count}
            
        elif cmd_type == 'repeat':
            times = int(match.group(1))
            variables = {'times': times}
            
        elif cmd_type == 'wait':
            duration = int(match.group(1))
            # Check if it's seconds or milliseconds from the pattern
            if 's' in match.group(0) and 'ms' not in match.group(0):
                duration *= 1000  # Convert to milliseconds
            variables = {'duration': duration}
            
        elif cmd_type == 'type_text':
            text = match.group(1)
            variables = {'text': text}
            
        elif cmd_type == 'press_key':
            key = match.group(1)
            variables = {'key': key}
            
        elif cmd_type == 'click':
            if match.lastindex >= 2:
                # Position click
                x = int(match.group(1))
                y = int(match.group(2))
                variables = {'x': x, 'y': y, 'button': 'left'}
            else:
                # Button click
                button = match.group(1)
                variables = {'button': button}
                
        elif cmd_type == 'open':
            target = match.group(1)
            variables = {'target': target}
        
        return variables
    
    def parse_template_variables(self, text: str) -> List[str]:
        """
        Extract variable names from a template string
        Example: "Hello {name}, you have {count} messages" -> ['name', 'count']
        """
        return re.findall(r'\{(\w+)\}', text)
    
    def substitute_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Substitute variables in a template string
        Example: "Hello {name}" with {'name': 'John'} -> "Hello John"
        """
        for var_name, var_value in variables.items():
            text = text.replace(f"{{{var_name}}}", str(var_value))
        return text


class DynamicMacroGenerator:
    """Generate macro actions from parsed commands"""
    
    def __init__(self):
        self.parser = DynamicMacroParser()
    
    def generate_actions(self, command: str):
        """
        Generate a list of macro actions from a natural language command
        Returns: List of MacroAction objects
        """
        from macro_manager import MacroAction
        
        cmd_type, variables = self.parser.parse_command(command)
        
        if not cmd_type:
            return []
        
        actions = []
        
        if cmd_type == 'delete_words':
            count = variables.get('count', 1)
            # Delete last N words: Select N words back then delete
            for _ in range(count):
                actions.append(MacroAction("Keyboard Press", {"key": "ctrl+shift+left"}))
            actions.append(MacroAction("Keyboard Press", {"key": "delete"}))
            
        elif cmd_type == 'repeat':
            # This would need special handling in the executor
            # For now, just store the repeat count
            actions.append(MacroAction("Wait", {"duration": 0, "repeat": variables.get('times', 1)}))
            
        elif cmd_type == 'wait':
            duration = variables.get('duration', 100)
            actions.append(MacroAction("Wait", {"duration": duration}))
            
        elif cmd_type == 'type_text':
            text = variables.get('text', '')
            actions.append(MacroAction("Text Paste", {"text": text}))
            
        elif cmd_type == 'press_key':
            key = variables.get('key', '')
            actions.append(MacroAction("Keyboard Press", {"key": key}))
            
        elif cmd_type == 'click':
            x = variables.get('x', 0)
            y = variables.get('y', 0)
            button = variables.get('button', 'left')
            if x or y:
                actions.append(MacroAction("Mouse Click", {
                    "button": button.capitalize(),
                    "x": x,
                    "y": y,
                    "relative": False
                }))
            else:
                actions.append(MacroAction("Mouse Click", {
                    "button": button.capitalize(),
                    "x": 0,
                    "y": 0,
                    "relative": True
                }))
                
        elif cmd_type == 'open':
            target = variables.get('target', '')
            # Try to determine if it's a URL, file, or application
            if target.startswith('http://') or target.startswith('https://'):
                actions.append(MacroAction("Open URL", {"url": target}))
            elif '.' in target and '/' in target:
                actions.append(MacroAction("Open File", {"path": target}))
            else:
                actions.append(MacroAction("Open Application", {
                    "app_path": target,
                    "args": ""
                }))
        
        return actions


class DynamicMacroExecutor:
    """Execute dynamic macros with runtime variable substitution"""
    
    def __init__(self, base_executor):
        self.base_executor = base_executor
        self.parser = DynamicMacroParser()
    
    def execute_dynamic_macro(self, macro, user_input: str):
        """
        Execute a dynamic macro with user-provided input
        The user_input string is parsed for variables which are then used in the macro
        """
        # Parse the user input to extract variables
        cmd_type, variables = self.parser.parse_command(user_input)
        
        # If the macro has template variables, try to extract them from input
        if not variables:
            # Try to extract any numbers from the input
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                # Create generic variables
                for i, num in enumerate(numbers):
                    variables[f'var{i+1}'] = int(num)
                    variables['count'] = int(numbers[0])  # Most common use case
        
        # Execute the macro with the extracted variables
        self.base_executor.execute_macro(macro, variables)
    
    def create_macro_from_command(self, command: str):
        """
        Create a new macro from a natural language command
        Returns: Macro object
        """
        from macro_manager import Macro
        
        generator = DynamicMacroGenerator()
        actions = generator.generate_actions(command)
        
        # Create macro with the command as the name
        macro = Macro(
            name=command.capitalize(),
            actions=actions,
            dynamic=True
        )
        
        return macro


# Preset dynamic macro templates
PRESET_DYNAMIC_MACROS = {
    "Delete Last N Words": {
        "description": "Delete the last N words",
        "input_format": "delete last {count} words",
        "template": [
            {"action_type": "Keyboard Press", "params": {"key": "ctrl+shift+left", "repeat": "{count}"}},
            {"action_type": "Keyboard Press", "params": {"key": "delete"}}
        ]
    },
    "Wait N Milliseconds": {
        "description": "Wait for N milliseconds",
        "input_format": "wait {duration} ms",
        "template": [
            {"action_type": "Wait", "params": {"duration": "{duration}", "variable": True}}
        ]
    },
    "Repeat Action N Times": {
        "description": "Repeat the previous action N times",
        "input_format": "repeat {times} times",
        "template": []  # Special handling needed
    },
    "Move Cursor N Pixels": {
        "description": "Move mouse cursor N pixels in a direction",
        "input_format": "move {pixels} pixels {direction}",
        "template": [
            {"action_type": "Mouse Move", "params": {
                "x": "{pixels}",  # Calculated based on direction
                "y": "{pixels}",  # Calculated based on direction
                "relative": True
            }}
        ]
    },
    "Select N Lines": {
        "description": "Select N lines of text",
        "input_format": "select {count} lines",
        "template": [
            {"action_type": "Keyboard Press", "params": {"key": "home"}},
            {"action_type": "Keyboard Press", "params": {"key": "shift+down", "repeat": "{count}"}},
        ]
    }
}


# Example usage
if __name__ == "__main__":
    parser = DynamicMacroParser()
    
    # Test various commands
    test_commands = [
        "delete last 3 words",
        "wait 500 milliseconds",
        "type 'Hello World'",
        "click at 100, 200",
        "open notepad",
        "repeat 5 times",
    ]
    
    print("Testing Dynamic Macro Parser:\n")
    for cmd in test_commands:
        cmd_type, variables = parser.parse_command(cmd)
        print(f"Command: {cmd}")
        print(f"  Type: {cmd_type}")
        print(f"  Variables: {variables}\n")
    
    # Test macro generation
    print("\nTesting Macro Generation:\n")
    generator = DynamicMacroGenerator()
    
    for cmd in test_commands:
        actions = generator.generate_actions(cmd)
        print(f"Command: {cmd}")
        print(f"  Generated {len(actions)} action(s)")
        for i, action in enumerate(actions, 1):
            print(f"    {i}. {action}")
        print()

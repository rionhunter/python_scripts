"""
Macro Executor - Execute macro actions
Handles all macro output types: keyboard, mouse, clipboard, applications, scripts
"""

import subprocess
import time
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional
import pyperclip


class MacroExecutor:
    """Executes macro actions"""
    
    def __init__(self):
        self.is_executing = False
        
    def execute_action(self, action_type: str, params: Dict[str, Any], variables: Optional[Dict[str, Any]] = None):
        """Execute a single macro action"""
        variables = variables or {}
        
        try:
            if action_type == "Keyboard Press":
                self._keyboard_press(params)
            elif action_type == "Text Paste":
                self._text_paste(params, variables)
            elif action_type == "Mouse Click":
                self._mouse_click(params)
            elif action_type == "Mouse Move":
                self._mouse_move(params)
            elif action_type == "Wait":
                self._wait(params, variables)
            elif action_type == "Open File":
                self._open_file(params)
            elif action_type == "Open URL":
                self._open_url(params)
            elif action_type == "Open Application":
                self._open_application(params)
            elif action_type == "Switch Application":
                self._switch_application(params)
            elif action_type == "Run Script":
                self._run_script(params)
            else:
                print(f"Unknown action type: {action_type}")
                
        except Exception as e:
            print(f"Error executing {action_type}: {e}")
            raise
    
    def _keyboard_press(self, params: Dict[str, Any]):
        """Execute keyboard press action"""
        try:
            import keyboard
            
            key = params.get('key', '')
            hold = params.get('hold', False)
            
            if not key:
                return
            
            if hold:
                keyboard.press(key)
            else:
                keyboard.send(key)
                
        except ImportError:
            print("keyboard library not installed. Install with: pip install keyboard")
        except Exception as e:
            print(f"Keyboard press error: {e}")
    
    def _text_paste(self, params: Dict[str, Any], variables: Dict[str, Any]):
        """Execute text paste action"""
        text = params.get('text', '')
        has_variables = params.get('has_variables', False)
        
        # Replace variables in text
        if has_variables:
            for var_name, var_value in variables.items():
                text = text.replace(f"{{{var_name}}}", str(var_value))
        
        # Copy to clipboard
        pyperclip.copy(text)
        
        # Simulate Ctrl+V
        try:
            import keyboard
            keyboard.send('ctrl+v')
        except ImportError:
            print("keyboard library not installed. Text copied to clipboard but not pasted.")
    
    def _mouse_click(self, params: Dict[str, Any]):
        """Execute mouse click action"""
        try:
            import pyautogui
            
            button = params.get('button', 'Left').lower()
            x = params.get('x', 0)
            y = params.get('y', 0)
            relative = params.get('relative', False)
            double = params.get('double', False)
            
            if relative:
                current_x, current_y = pyautogui.position()
                x += current_x
                y += current_y
            
            # Move to position
            if x != 0 or y != 0:
                pyautogui.moveTo(x, y)
            
            # Click
            clicks = 2 if double else 1
            pyautogui.click(button=button, clicks=clicks)
            
        except ImportError:
            print("pyautogui library not installed. Install with: pip install pyautogui")
        except Exception as e:
            print(f"Mouse click error: {e}")
    
    def _mouse_move(self, params: Dict[str, Any]):
        """Execute mouse move action"""
        try:
            import pyautogui
            
            x = params.get('x', 0)
            y = params.get('y', 0)
            relative = params.get('relative', False)
            duration = params.get('duration', 100) / 1000.0  # Convert to seconds
            
            if relative:
                current_x, current_y = pyautogui.position()
                x += current_x
                y += current_y
            
            pyautogui.moveTo(x, y, duration=duration)
            
        except ImportError:
            print("pyautogui library not installed. Install with: pip install pyautogui")
        except Exception as e:
            print(f"Mouse move error: {e}")
    
    def _wait(self, params: Dict[str, Any], variables: Dict[str, Any]):
        """Execute wait action"""
        duration = params.get('duration', 100)
        variable = params.get('variable', False)
        
        # If variable, try to get from variables dict
        if variable and 'wait_duration' in variables:
            duration = variables['wait_duration']
        
        time.sleep(duration / 1000.0)  # Convert to seconds
    
    def _open_file(self, params: Dict[str, Any]):
        """Execute open file action"""
        file_path = params.get('path', '')
        
        if not file_path or not Path(file_path).exists():
            print(f"File not found: {file_path}")
            return
        
        try:
            import os
            import platform
            
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(file_path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
                
        except Exception as e:
            print(f"Error opening file: {e}")
    
    def _open_url(self, params: Dict[str, Any]):
        """Execute open URL action"""
        url = params.get('url', '')
        
        if not url:
            return
        
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening URL: {e}")
    
    def _open_application(self, params: Dict[str, Any]):
        """Execute open application action"""
        app_path = params.get('app_path', '')
        args = params.get('args', '')
        
        if not app_path:
            return
        
        try:
            cmd = [app_path]
            if args:
                # Simple argument splitting (you might want more sophisticated parsing)
                cmd.extend(args.split())
            
            subprocess.Popen(cmd, shell=False)
            
        except Exception as e:
            print(f"Error opening application: {e}")
    
    def _switch_application(self, params: Dict[str, Any]):
        """Execute switch application action"""
        app_name = params.get('app_name', '')
        match_by = params.get('match_by', 'Name')
        
        if not app_name:
            return
        
        try:
            import platform
            
            system = platform.system()
            
            if system == 'Windows':
                self._switch_app_windows(app_name, match_by)
            elif system == 'Darwin':
                self._switch_app_macos(app_name)
            else:
                self._switch_app_linux(app_name)
                
        except Exception as e:
            print(f"Error switching application: {e}")
    
    def _switch_app_windows(self, app_name: str, match_by: str):
        """Switch to application on Windows"""
        try:
            import pygetwindow as gw
            
            # Get all windows
            windows = gw.getAllWindows()
            
            # Find matching window
            for window in windows:
                if match_by == "Most Recent":
                    # Just activate the first visible window
                    if window.visible and window.title:
                        window.activate()
                        return
                elif match_by == "Title":
                    if app_name.lower() in window.title.lower():
                        window.activate()
                        return
                else:  # Name or Class
                    if app_name.lower() in window.title.lower():
                        window.activate()
                        return
            
            print(f"Window not found: {app_name}")
            
        except ImportError:
            print("pygetwindow library not installed. Install with: pip install pygetwindow")
        except Exception as e:
            print(f"Error switching window: {e}")
    
    def _switch_app_macos(self, app_name: str):
        """Switch to application on macOS"""
        try:
            script = f'tell application "{app_name}" to activate'
            subprocess.run(['osascript', '-e', script])
        except Exception as e:
            print(f"Error switching app on macOS: {e}")
    
    def _switch_app_linux(self, app_name: str):
        """Switch to application on Linux"""
        try:
            # Use wmctrl if available
            subprocess.run(['wmctrl', '-a', app_name])
        except FileNotFoundError:
            print("wmctrl not found. Install with: sudo apt install wmctrl")
        except Exception as e:
            print(f"Error switching app on Linux: {e}")
    
    def _run_script(self, params: Dict[str, Any]):
        """Execute run script action"""
        script_path = params.get('script_path', '')
        args = params.get('args', '')
        
        if not script_path or not Path(script_path).exists():
            print(f"Script not found: {script_path}")
            return
        
        try:
            # Determine how to run the script based on extension
            script_path = Path(script_path)
            
            if script_path.suffix == '.py':
                cmd = ['python', str(script_path)]
            elif script_path.suffix == '.bat':
                cmd = [str(script_path)]
            elif script_path.suffix == '.sh':
                cmd = ['bash', str(script_path)]
            else:
                cmd = [str(script_path)]
            
            if args:
                cmd.extend(args.split())
            
            subprocess.Popen(cmd, shell=False)
            
        except Exception as e:
            print(f"Error running script: {e}")
    
    def execute_macro(self, macro, variables: Optional[Dict[str, Any]] = None):
        """Execute a complete macro"""
        self.is_executing = True
        variables = variables or {}
        
        try:
            for action in macro.actions:
                if not self.is_executing:
                    break
                
                self.execute_action(action.action_type, action.params, variables)
                
        except Exception as e:
            print(f"Error executing macro: {e}")
        finally:
            self.is_executing = False
    
    def stop(self):
        """Stop macro execution"""
        self.is_executing = False


# Example usage
if __name__ == "__main__":
    from macro_manager import MacroAction, Macro
    
    # Create a simple test macro
    macro = Macro(name="Test Macro")
    
    # Add some actions
    macro.actions.append(MacroAction("Text Paste", {
        "text": "Hello from Macro Manager!",
        "has_variables": False
    }))
    
    macro.actions.append(MacroAction("Wait", {"duration": 500}))
    
    macro.actions.append(MacroAction("Open URL", {
        "url": "https://github.com"
    }))
    
    # Execute the macro
    executor = MacroExecutor()
    print("Executing test macro...")
    executor.execute_macro(macro)
    print("Done!")

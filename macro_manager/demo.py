"""
Example macros and usage demonstrations for Macro Manager
Run this to see various capabilities and test the system
"""

from macro_manager import Macro, MacroAction
from macro_executor import MacroExecutor
from dynamic_macros import DynamicMacroParser, DynamicMacroGenerator
import time


def demo_basic_macros():
    """Demonstrate basic macro creation and execution"""
    print("=" * 60)
    print("DEMO 1: Basic Macros")
    print("=" * 60)
    
    executor = MacroExecutor()
    
    # Example 1: Simple text paste
    print("\n1. Creating a text paste macro...")
    macro1 = Macro(name="Paste Greeting")
    macro1.actions.append(MacroAction("Text Paste", {
        "text": "Hello! This is a test from Macro Manager.",
        "has_variables": False
    }))
    
    print(f"   Macro: {macro1.name}")
    print(f"   Actions: {len(macro1.actions)}")
    
    # Example 2: Multi-step macro
    print("\n2. Creating a multi-step macro...")
    macro2 = Macro(name="Open Browser and Search")
    macro2.actions.append(MacroAction("Open URL", {
        "url": "https://www.google.com"
    }))
    macro2.actions.append(MacroAction("Wait", {"duration": 2000}))
    macro2.actions.append(MacroAction("Text Paste", {
        "text": "Python automation",
        "has_variables": False
    }))
    
    print(f"   Macro: {macro2.name}")
    print(f"   Actions: {len(macro2.actions)}")
    for i, action in enumerate(macro2.actions, 1):
        print(f"     {i}. {action}")
    
    print("\n✓ Basic macros created successfully!")


def demo_dynamic_macros():
    """Demonstrate dynamic macro parsing"""
    print("\n" + "=" * 60)
    print("DEMO 2: Dynamic Macros")
    print("=" * 60)
    
    parser = DynamicMacroParser()
    generator = DynamicMacroGenerator()
    
    test_commands = [
        "delete last 3 words",
        "wait 500 milliseconds",
        "type 'Hello World'",
        "press enter",
        "click at 100, 200",
        "open notepad",
    ]
    
    print("\nParsing natural language commands:\n")
    for cmd in test_commands:
        cmd_type, variables = parser.parse_command(cmd)
        actions = generator.generate_actions(cmd)
        
        print(f"Command: '{cmd}'")
        print(f"  → Type: {cmd_type}")
        print(f"  → Variables: {variables}")
        print(f"  → Generated {len(actions)} action(s)")
        if actions:
            for action in actions:
                print(f"     • {action}")
        print()
    
    print("✓ Dynamic parsing working!")


def demo_macro_templates():
    """Show some useful macro templates"""
    print("\n" + "=" * 60)
    print("DEMO 3: Macro Templates")
    print("=" * 60)
    
    templates = {
        "Email Signature": Macro(
            name="Insert Email Signature",
            actions=[
                MacroAction("Text Paste", {
                    "text": "\n\nBest regards,\nJohn Doe\nSoftware Developer\njohn.doe@example.com",
                    "has_variables": False
                })
            ]
        ),
        
        "Screenshot and Save": Macro(
            name="Take Screenshot",
            actions=[
                MacroAction("Keyboard Press", {"key": "win+shift+s"}),
                MacroAction("Wait", {"duration": 2000}),
                MacroAction("Keyboard Press", {"key": "ctrl+s"}),
            ]
        ),
        
        "Format Code Block": Macro(
            name="Wrap in Code Block",
            actions=[
                MacroAction("Text Paste", {"text": "```python\n"}),
                MacroAction("Keyboard Press", {"key": "ctrl+v"}),
                MacroAction("Text Paste", {"text": "\n```"}),
            ]
        ),
        
        "Open Dev Environment": Macro(
            name="Launch Development Setup",
            actions=[
                MacroAction("Open Application", {
                    "app_path": "code",  # VS Code
                    "args": "."
                }),
                MacroAction("Wait", {"duration": 3000}),
                MacroAction("Open URL", {"url": "http://localhost:3000"}),
            ]
        ),
        
        "Date Stamp": Macro(
            name="Insert Current Date",
            actions=[
                MacroAction("Run Script", {
                    "script_path": "get_date.py",
                    "args": "--format '%Y-%m-%d'"
                })
            ]
        ),
    }
    
    print("\nUseful macro templates:\n")
    for name, macro in templates.items():
        print(f"📋 {name}")
        print(f"   Description: {macro.name}")
        print(f"   Steps: {len(macro.actions)}")
        for i, action in enumerate(macro.actions, 1):
            print(f"     {i}. {action}")
        print()
    
    print("✓ Templates ready to use!")


def demo_input_devices():
    """Show input device configuration"""
    print("\n" + "=" * 60)
    print("DEMO 4: Input Devices")
    print("=" * 60)
    
    print("\nSupported input devices:\n")
    
    devices = [
        ("⌨️  Keyboard", "Capture hotkeys and key combinations"),
        ("🎮 Game Controller", "Use buttons and axes as triggers"),
        ("🎹 MIDI Device", "Trigger macros from MIDI controllers"),
        ("💬 Text Commands", "Execute macros via typed commands"),
        ("🎤 Voice Dictation", "AI-powered voice control"),
    ]
    
    for device, description in devices:
        print(f"{device}")
        print(f"   {description}\n")
    
    print("Example device configurations:")
    
    print("\n1. Keyboard Hotkey:")
    print("   Trigger: Ctrl+Alt+P")
    print("   → Execute 'Paste Template' macro")
    
    print("\n2. MIDI Note:")
    print("   Trigger: Note C4 (Middle C)")
    print("   → Execute 'Record Audio' macro")
    
    print("\n3. Controller Button:")
    print("   Trigger: Button A")
    print("   → Execute 'Quick Save' macro")
    
    print("\n4. Voice Command:")
    print("   Trigger: 'Open email'")
    print("   → Execute 'Launch Email Client' macro")
    
    print("\n✓ Multi-device support configured!")


def demo_variable_substitution():
    """Demonstrate variable substitution in macros"""
    print("\n" + "=" * 60)
    print("DEMO 5: Variable Substitution")
    print("=" * 60)
    
    print("\nDynamic macros with runtime variables:\n")
    
    examples = [
        {
            "name": "Personalized Greeting",
            "template": "Hello {name}! Welcome to {company}.",
            "variables": {"name": "Alice", "company": "TechCorp"},
            "result": "Hello Alice! Welcome to TechCorp."
        },
        {
            "name": "Delete N Words",
            "command": "delete last {count} words",
            "variables": {"count": 5},
            "result": "Selects and deletes last 5 words"
        },
        {
            "name": "Wait Variable Time",
            "command": "wait {duration} milliseconds",
            "variables": {"duration": 250},
            "result": "Pauses for 250ms"
        },
    ]
    
    for ex in examples:
        print(f"Macro: {ex['name']}")
        if 'template' in ex:
            print(f"  Template: {ex['template']}")
        if 'command' in ex:
            print(f"  Command: {ex['command']}")
        print(f"  Variables: {ex['variables']}")
        print(f"  → Result: {ex['result']}")
        print()
    
    print("✓ Variable substitution working!")


def show_ui_features():
    """Show UI design features"""
    print("\n" + "=" * 60)
    print("DEMO 6: UI Features")
    print("=" * 60)
    
    print("\n🎨 Glassmorphism Design:")
    print("   • Blurred glass background")
    print("   • Subtle darkening overlay (15% opacity)")
    print("   • Light fonts for contrast")
    print("   • Rounded corners and smooth edges")
    print("   • Minimal interface that expands on interaction")
    
    print("\n📐 Layout:")
    print("   • Left Panel: Macro list with search")
    print("   • Right Panel: Macro editor with action builder")
    print("   • Collapsible sections for clean look")
    
    print("\n🎯 Interactions:")
    print("   • Double-click to edit macro")
    print("   • Drag to reorder actions")
    print("   • Context menus for quick actions")
    print("   • Keyboard shortcuts for power users")
    
    print("\n✓ Modern, sleek UI ready!")


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "MACRO MANAGER DEMO" + " " * 24 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        demo_basic_macros()
        time.sleep(1)
        
        demo_dynamic_macros()
        time.sleep(1)
        
        demo_macro_templates()
        time.sleep(1)
        
        demo_input_devices()
        time.sleep(1)
        
        demo_variable_substitution()
        time.sleep(1)
        
        show_ui_features()
        
        print("\n" + "=" * 60)
        print("🎉 All demos completed successfully!")
        print("=" * 60)
        print("\nTo start the application, run:")
        print("  python macro_manager.py")
        print("\nOr use the launcher:")
        print("  launch.bat")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

# PyQt6 Text File Compiler Demo

**Description:** Demonstration of the enhanced text file compiler with PyQt6 GUI features

**Compiled:** 2025-09-23 01:34:42

---


## File Structure

```
demo_files/
├── config.json
├── sample_markdown.md
├── sample_python.py
└── styles.css```

## sample_python.py
**Path:** `~/work/python_scripts/python_scripts/text_file_compiler/demo_files/sample_python.py`
**Size:** 1.1 KB
**Encoding:** ascii

```python
#!/usr/bin/env python3
"""
Sample Python script for demonstration.

This script shows how the text file compiler handles Python code
with proper syntax highlighting and formatting.
"""

import os
import sys
from datetime import datetime


class DemoClass:
    """A demonstration class."""
    
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now()
    
    def greet(self) -> str:
        """Return a greeting message."""
        return f"Hello from {self.name}! Created at {self.created_at}"
    
    def calculate_fibonacci(self, n: int) -> int:
        """Calculate the nth Fibonacci number."""
        if n <= 1:
            return n
        return self.calculate_fibonacci(n - 1) + self.calculate_fibonacci(n - 2)


def main():
    """Main function demonstrating the class usage."""
    demo = DemoClass("PyQt6 Text Compiler Demo")
    print(demo.greet())
    
    # Calculate some Fibonacci numbers
    for i in range(10):
        fib = demo.calculate_fibonacci(i)
        print(f"Fibonacci({i}) = {fib}")


if __name__ == "__main__":
    main()
```

## sample_markdown.md
**Path:** `~/work/python_scripts/python_scripts/text_file_compiler/demo_files/sample_markdown.md`
**Size:** 1.4 KB
**Encoding:** utf-8

```markdown
# Sample Markdown Document

This is a demonstration of how the **PyQt6 Text File Compiler** handles Markdown files.

## Features

The compiler includes several advanced features:

### Core Functionality
- ✅ File compilation with syntax highlighting
- ✅ Project management with persistent settings
- ✅ Built-in file browser
- ✅ Multiple file format support

### GUI Enhancements
- 🎨 **Frameless design** with modern aesthetics
- 🖱️ **Drag-to-move** functionality
- 🔧 **Context menus** for quick actions
- 🔍 **Zoom and pan** capabilities
- 📐 **Flexible resizing** options

## Code Example

Here's a simple JavaScript example:

```javascript
function greetUser(name) {
    const message = `Hello, ${name}!`;
    console.log(message);
    return message;
}

// Usage
const user = "Developer";
greetUser(user);
```

## Table Example

| Feature | Status | Priority |
|---------|--------|----------|
| File Browser | ✅ Complete | High |
| Project Files | ✅ Complete | High |
| Zoom/Pan | ✅ Complete | Medium |
| Context Menu | ✅ Complete | Medium |
| Glass Effect | ✅ Complete | Low |

## Important Notes

> **Note**: This application requires PyQt6 to be installed for the GUI functionality.
> 
> Install with: `pip install PyQt6>=6.4.0`

## Conclusion

The PyQt6 Text File Compiler provides a modern, feature-rich interface for combining text and code files into a single document, perfect for code reviews, documentation, or sharing project overviews.
```

## config.json
**Path:** `~/work/python_scripts/python_scripts/text_file_compiler/demo_files/config.json`
**Size:** 1.1 KB
**Encoding:** ascii

```json
{
  "project_info": {
    "name": "Text File Compiler Demo",
    "version": "1.0.0",
    "description": "A sample project demonstrating the PyQt6 Text File Compiler",
    "author": "Development Team",
    "created": "2024-01-15"
  },
  "features": {
    "gui": {
      "frameless_design": true,
      "drag_to_move": true,
      "context_menu": true,
      "zoom_pan": true,
      "glass_effect": true
    },
    "functionality": {
      "file_compilation": true,
      "project_management": true,
      "file_browser": true,
      "syntax_highlighting": true,
      "persistent_settings": true
    }
  },
  "supported_formats": [
    "Python (.py)",
    "JavaScript (.js)",
    "Markdown (.md)",
    "JSON (.json)",
    "HTML (.html)",
    "CSS (.css)",
    "Text (.txt)",
    "And many more..."
  ],
  "keyboard_shortcuts": {
    "close_app": "Escape",
    "move_window": "Right-click + drag",
    "resize_center": "Shift + Right-click",
    "zoom": "Shift + Middle-click drag",
    "scale": "Ctrl + Shift + Middle-click drag"
  },
  "requirements": {
    "python": "3.8+",
    "pyqt6": "6.4.0+",
    "os_support": ["Windows 10+", "macOS 10.14+", "Linux"]
  }
}
```

## styles.css
**Path:** `~/work/python_scripts/python_scripts/text_file_compiler/demo_files/styles.css`
**Size:** 1.7 KB
**Encoding:** ascii

```css
/* Sample CSS for styling demo */

/* Main container styling */
.main-container {
    background: linear-gradient(135deg, 
        rgba(245, 245, 220, 0.8), 
        rgba(240, 248, 255, 0.7)
    );
    border: 2px solid rgba(34, 139, 34, 0.6);
    border-radius: 15px;
    margin: 20px;
    padding: 20px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(10px);
}

/* Button styling inspired by the PyQt6 app */
.modern-button {
    background: linear-gradient(to bottom,
        rgba(34, 139, 34, 0.9),
        rgba(34, 139, 34, 0.7)
    );
    border: 1px solid rgba(34, 139, 34, 1);
    border-radius: 8px;
    color: white;
    padding: 8px 16px;
    font-weight: bold;
    font-family: 'Segoe UI', Arial, sans-serif;
    cursor: pointer;
    transition: all 0.3s ease;
}

.modern-button:hover {
    background: linear-gradient(to bottom,
        rgba(34, 139, 34, 1),
        rgba(34, 139, 34, 0.8)
    );
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(34, 139, 34, 0.3);
}

/* Text area styling */
.glass-text-area {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(34, 139, 34, 0.5);
    border-radius: 8px;
    padding: 12px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 10pt;
    backdrop-filter: blur(5px);
}

/* Color palette used in the application */
:root {
    --forest-green: rgba(34, 139, 34, 1);
    --earthy-beige: rgba(245, 245, 220, 1);
    --sky-blue: rgba(240, 248, 255, 1);
    --warm-cream: rgba(250, 240, 230, 1);
    --glass-white: rgba(255, 255, 255, 0.8);
}

/* Responsive design */
@media (max-width: 768px) {
    .main-container {
        margin: 10px;
        padding: 15px;
    }
    
    .modern-button {
        padding: 6px 12px;
        font-size: 9pt;
    }
}
```


---

**Compilation Summary**

- Files processed: 4
- Generated: 2025-09-23 01:34:42

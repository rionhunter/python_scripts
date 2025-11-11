#!/usr/bin/env python3
"""
Image Processing Toolkit Launcher
Easy access to all image processing tools
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from pathlib import Path

class ImageToolkitLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing Toolkit")
        self.root.geometry("500x600")
        
        # Get the directory where this script is located
        self.script_dir = Path(__file__).parent
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Image Processing Toolkit", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=20)
        
        # Description
        desc_label = ttk.Label(main_frame, 
                              text="Choose a tool to launch:", 
                              font=('Arial', 12))
        desc_label.pack(pady=10)
        
        # Tools frame
        tools_frame = ttk.Frame(main_frame)
        tools_frame.pack(fill='both', expand=True, pady=20)
        
        # Tool buttons
        tools = [
            {
                "name": "RAW Converter",
                "description": "Convert RAW files to common formats\n(JPEG, PNG, TIFF, WEBP)",
                "script": "raw_converter.py",
                "icon": "📷"
            },
            {
                "name": "Image Converter", 
                "description": "Convert between image formats\nwith optimized settings",
                "script": "image_converter.py",
                "icon": "🔄"
            },
            {
                "name": "Filter System",
                "description": "Create and apply custom filters\nwith real-time preview",
                "script": "image_filter_system.py", 
                "icon": "🎨"
            },
            {
                "name": "Batch Processor",
                "description": "Chain multiple operations for\ncomplex batch workflows",
                "script": "batch_image_processor.py",
                "icon": "⚙️"
            }
        ]
        
        for i, tool in enumerate(tools):
            self.create_tool_button(tools_frame, tool, i)
        
        # Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', pady=20)
        
        # Additional options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill='x')
        
        # Install dependencies button
        ttk.Button(options_frame, text="Install Dependencies", 
                  command=self.install_dependencies).pack(side='left', padx=5)
        
        # Help button
        ttk.Button(options_frame, text="Help", 
                  command=self.show_help).pack(side='left', padx=5)
        
        # Exit button
        ttk.Button(options_frame, text="Exit", 
                  command=self.root.quit).pack(side='right', padx=5)
    
    def create_tool_button(self, parent, tool, index):
        # Tool frame
        tool_frame = ttk.LabelFrame(parent, text=f"{tool['icon']} {tool['name']}", 
                                   padding="10")
        tool_frame.pack(fill='x', pady=10)
        
        # Description
        desc_label = ttk.Label(tool_frame, text=tool['description'], 
                              font=('Arial', 10), foreground='gray')
        desc_label.pack(anchor='w')
        
        # Launch button
        launch_button = ttk.Button(tool_frame, text=f"Launch {tool['name']}", 
                                  command=lambda t=tool: self.launch_tool(t))
        launch_button.pack(anchor='e', pady=5)
    
    def launch_tool(self, tool):
        script_path = self.script_dir / tool['script']
        
        if not script_path.exists():
            messagebox.showerror("Error", f"Script not found: {tool['script']}")
            return
        
        try:
            # Launch the tool in a new process
            if sys.platform.startswith('win'):
                subprocess.Popen([sys.executable, str(script_path)], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen([sys.executable, str(script_path)])
            
            # Optionally minimize the launcher
            self.root.iconify()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {tool['name']}:\n{str(e)}")
    
    def install_dependencies(self):
        """Install required dependencies"""
        requirements_path = self.script_dir / "requirements.txt"
        
        if not requirements_path.exists():
            messagebox.showerror("Error", "requirements.txt not found")
            return
        
        # Show confirmation dialog
        if messagebox.askyesno("Install Dependencies", 
                              "This will install required Python packages using pip.\n\n"
                              "Continue?"):
            try:
                # Create a new window to show installation progress
                install_window = tk.Toplevel(self.root)
                install_window.title("Installing Dependencies")
                install_window.geometry("500x300")
                install_window.transient(self.root)
                install_window.grab_set()
                
                # Text widget to show output
                text_widget = tk.Text(install_window, wrap='word')
                text_widget.pack(fill='both', expand=True, padx=10, pady=10)
                
                scrollbar = ttk.Scrollbar(install_window, orient='vertical', 
                                        command=text_widget.yview)
                scrollbar.pack(side='right', fill='y')
                text_widget.configure(yscrollcommand=scrollbar.set)
                
                text_widget.insert('end', "Installing dependencies...\n\n")
                text_widget.update()
                
                # Run pip install
                process = subprocess.Popen(
                    [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_path)],
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Read output in real-time
                for line in process.stdout:
                    text_widget.insert('end', line)
                    text_widget.see('end')
                    text_widget.update()
                
                process.wait()
                
                if process.returncode == 0:
                    text_widget.insert('end', "\n✓ Dependencies installed successfully!")
                    messagebox.showinfo("Success", "Dependencies installed successfully!")
                else:
                    text_widget.insert('end', f"\n✗ Installation failed with code {process.returncode}")
                    messagebox.showerror("Error", "Installation failed. Check the output for details.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to install dependencies:\n{str(e)}")
    
    def show_help(self):
        """Show help information"""
        help_text = """
Image Processing Toolkit Help

This toolkit provides four main tools for image processing:

1. RAW Converter
   - Converts RAW camera files to common formats
   - Supports major camera brands (Canon, Nikon, Sony, etc.)
   - Batch processing capabilities

2. Image Converter  
   - Converts between common image formats
   - Format-specific optimizations
   - Quality control for lossy formats

3. Filter System
   - Create and apply custom image filters
   - Built-in presets (Vintage, Sepia, etc.)
   - Real-time preview
   - Save custom filter configurations

4. Batch Processor
   - Chain multiple operations together
   - Complex workflows (RAW → Convert → Filter)
   - Progress tracking and results logging

Requirements:
- Python 3.7 or later
- Required packages (install via 'Install Dependencies' button)

For detailed documentation, see README_image_processing.md
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Image Processing Toolkit")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        
        text_widget = tk.Text(help_window, wrap='word', padx=10, pady=10)
        text_widget.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(help_window, orient='vertical', command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert('1.0', help_text)
        text_widget.configure(state='disabled')  # Make read-only

def main():
    root = tk.Tk()
    app = ImageToolkitLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
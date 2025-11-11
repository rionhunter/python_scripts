#!/usr/bin/env python3
"""
Raw Image Converter
Converts RAW image files to common formats (JPEG, PNG, TIFF, WEBP)
Supports single file and batch processing
"""

import sys
import os
import rawpy
import imageio
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import threading
from pathlib import Path

class RawConverter:
    def __init__(self):
        self.supported_raw_formats = ['.arw', '.cr2', '.cr3', '.dng', '.nef', '.orf', '.raf', '.rw2', '.pef', '.srw']
        self.output_formats = {
            'JPEG': '.jpg',
            'PNG': '.png', 
            'TIFF': '.tiff',
            'WEBP': '.webp'
        }
        
    def is_raw_file(self, filepath):
        """Check if file is a supported RAW format"""
        return Path(filepath).suffix.lower() in self.supported_raw_formats
    
    def convert_single_raw(self, input_path, output_path=None, output_format='JPEG', quality=95):
        """
        Convert a single RAW file to specified format
        
        Args:
            input_path: Path to RAW file
            output_path: Output path (if None, uses input path with new extension)
            output_format: Output format ('JPEG', 'PNG', 'TIFF', 'WEBP')
            quality: Quality for JPEG/WEBP (1-100)
        """
        try:
            # Read RAW file
            with rawpy.imread(input_path) as raw:
                # Process RAW to RGB array
                rgb = raw.postprocess()
            
            # Convert to PIL Image
            image = Image.fromarray(rgb)
            
            # Generate output path if not provided
            if output_path is None:
                input_file = Path(input_path)
                output_path = input_file.with_suffix(self.output_formats[output_format])
            
            # Save with format-specific options
            if output_format == 'JPEG':
                image.save(output_path, 'JPEG', quality=quality, optimize=True)
            elif output_format == 'PNG':
                image.save(output_path, 'PNG', optimize=True)
            elif output_format == 'TIFF':
                image.save(output_path, 'TIFF', compression='lzw')
            elif output_format == 'WEBP':
                image.save(output_path, 'WEBP', quality=quality, method=6)
                
            return True, f"Converted: {os.path.basename(input_path)} -> {os.path.basename(output_path)}"
            
        except Exception as e:
            return False, f"Error converting {os.path.basename(input_path)}: {str(e)}"
    
    def batch_convert(self, input_folder, output_folder=None, output_format='JPEG', quality=95, progress_callback=None):
        """
        Batch convert RAW files in a folder
        
        Args:
            input_folder: Folder containing RAW files
            output_folder: Output folder (if None, uses input folder)
            output_format: Target format
            quality: Quality setting
            progress_callback: Function to call with progress updates
        """
        if output_folder is None:
            output_folder = input_folder
            
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Find all RAW files
        raw_files = []
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if self.is_raw_file(file):
                    raw_files.append(os.path.join(root, file))
        
        results = []
        total_files = len(raw_files)
        
        for i, raw_file in enumerate(raw_files):
            if progress_callback:
                progress_callback(i, total_files, os.path.basename(raw_file))
            
            # Generate output path maintaining folder structure
            rel_path = os.path.relpath(raw_file, input_folder)
            output_path = os.path.join(output_folder, rel_path)
            output_path = Path(output_path).with_suffix(self.output_formats[output_format])
            
            # Create output subdirectory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            success, message = self.convert_single_raw(raw_file, str(output_path), output_format, quality)
            results.append((success, message))
        
        return results

class RawConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RAW Image Converter")
        self.root.geometry("600x500")
        
        self.converter = RawConverter()
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Mode selection
        ttk.Label(main_frame, text="Conversion Mode:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mode_var = tk.StringVar(value="single")
        ttk.Radiobutton(main_frame, text="Single File", variable=self.mode_var, value="single").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="Batch Folder", variable=self.mode_var, value="batch").grid(row=0, column=2, sticky=tk.W)
        
        # File/Folder selection
        ttk.Label(main_frame, text="Input:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_path_var, width=50).grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=1, column=3, padx=5)
        
        # Output folder
        ttk.Label(main_frame, text="Output:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_path_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_path_var, width=50).grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output).grid(row=2, column=3, padx=5)
        
        # Format selection
        ttk.Label(main_frame, text="Output Format:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="JPEG")
        format_combo = ttk.Combobox(main_frame, textvariable=self.format_var, values=list(self.converter.output_formats.keys()), state="readonly")
        format_combo.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # Quality setting
        ttk.Label(main_frame, text="Quality (JPEG/WEBP):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.IntVar(value=95)
        quality_scale = ttk.Scale(main_frame, from_=1, to=100, variable=self.quality_var, orient=tk.HORIZONTAL)
        quality_scale.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5)
        self.quality_label = ttk.Label(main_frame, text="95")
        self.quality_label.grid(row=4, column=2, sticky=tk.W)
        quality_scale.configure(command=self.update_quality_label)
        
        # Convert button
        ttk.Button(main_frame, text="Convert", command=self.start_conversion).grid(row=5, column=1, pady=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=7, column=0, columnspan=4, pady=5)
        
        # Results text area
        self.results_text = tk.Text(main_frame, height=10, width=70)
        self.results_text.grid(row=8, column=0, columnspan=4, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=8, column=4, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
    
    def update_quality_label(self, value):
        self.quality_label.config(text=str(int(float(value))))
    
    def browse_input(self):
        if self.mode_var.get() == "single":
            filename = filedialog.askopenfilename(
                title="Select RAW file",
                filetypes=[("RAW files", " ".join(f"*{ext}" for ext in self.converter.supported_raw_formats)),
                          ("All files", "*.*")]
            )
            if filename:
                self.input_path_var.set(filename)
        else:
            folder = filedialog.askdirectory(title="Select folder containing RAW files")
            if folder:
                self.input_path_var.set(folder)
    
    def browse_output(self):
        if self.mode_var.get() == "single":
            filename = filedialog.asksaveasfilename(
                title="Save converted file as",
                defaultextension=self.converter.output_formats[self.format_var.get()],
                filetypes=[(f"{self.format_var.get()} files", f"*{self.converter.output_formats[self.format_var.get()]}")]
            )
            if filename:
                self.output_path_var.set(filename)
        else:
            folder = filedialog.askdirectory(title="Select output folder")
            if folder:
                self.output_path_var.set(folder)
    
    def progress_callback(self, current, total, filename):
        progress = (current / total) * 100
        self.progress_var.set(progress)
        self.status_var.set(f"Processing: {filename} ({current+1}/{total})")
        self.root.update_idletasks()
    
    def start_conversion(self):
        if not self.input_path_var.get():
            messagebox.showerror("Error", "Please select input file/folder")
            return
            
        # Start conversion in separate thread
        thread = threading.Thread(target=self.convert)
        thread.daemon = True
        thread.start()
    
    def convert(self):
        try:
            self.results_text.delete(1.0, tk.END)
            self.progress_var.set(0)
            
            if self.mode_var.get() == "single":
                # Single file conversion
                input_path = self.input_path_var.get()
                output_path = self.output_path_var.get() if self.output_path_var.get() else None
                
                self.status_var.set("Converting...")
                success, message = self.converter.convert_single_raw(
                    input_path, output_path, self.format_var.get(), self.quality_var.get()
                )
                
                self.results_text.insert(tk.END, message + "\n")
                self.progress_var.set(100)
                self.status_var.set("Complete" if success else "Error")
                
            else:
                # Batch conversion
                input_folder = self.input_path_var.get()
                output_folder = self.output_path_var.get() if self.output_path_var.get() else None
                
                results = self.converter.batch_convert(
                    input_folder, output_folder, self.format_var.get(), 
                    self.quality_var.get(), self.progress_callback
                )
                
                # Display results
                success_count = sum(1 for success, _ in results if success)
                total_count = len(results)
                
                self.results_text.insert(tk.END, f"Batch conversion complete: {success_count}/{total_count} successful\n\n")
                
                for success, message in results:
                    self.results_text.insert(tk.END, f"{'✓' if success else '✗'} {message}\n")
                
                self.progress_var.set(100)
                self.status_var.set(f"Complete: {success_count}/{total_count} successful")
                
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")
            self.status_var.set("Error")

def main():
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Command line mode
        converter = RawConverter()
        
        if len(sys.argv) == 2:
            # Single file with default settings
            input_file = sys.argv[1]
            success, message = converter.convert_single_raw(input_file)
            print(message)
        else:
            print("Usage: python raw_converter.py [input_file]")
            print("Or run without arguments for GUI mode")
    else:
        # GUI mode
        root = tk.Tk()
        app = RawConverterGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
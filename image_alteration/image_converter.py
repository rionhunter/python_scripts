#!/usr/bin/env python3
"""
Image Format Converter
Converts between common image formats (JPEG, PNG, TIFF, WEBP, BMP, GIF)
Supports single file and batch processing with format-specific options
"""

import sys
import os
from PIL import Image, ImageOps
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from pathlib import Path

class ImageConverter:
    def __init__(self):
        self.input_formats = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.webp', '.bmp', '.gif', '.ico']
        self.output_formats = {
            'JPEG': ('.jpg', {'quality': 95, 'optimize': True}),
            'PNG': ('.png', {'optimize': True}),
            'TIFF': ('.tiff', {'compression': 'lzw'}),
            'WEBP': ('.webp', {'quality': 95, 'method': 6}),
            'BMP': ('.bmp', {}),
            'GIF': ('.gif', {'optimize': True}),
            'ICO': ('.ico', {})
        }
        
    def is_supported_format(self, filepath):
        """Check if file is a supported image format"""
        return Path(filepath).suffix.lower() in self.input_formats
    
    def convert_single_image(self, input_path, output_path=None, output_format='JPEG', **options):
        """
        Convert a single image file to specified format
        
        Args:
            input_path: Path to input image
            output_path: Output path (if None, uses input path with new extension)
            output_format: Target format
            **options: Format-specific options
        """
        try:
            # Open image
            with Image.open(input_path) as image:
                # Handle format-specific conversions
                if output_format == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
                    # Convert to RGB for JPEG (no transparency support)
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    
                    # Create white background
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                    else:
                        background.paste(image)
                    image = background
                
                elif output_format == 'PNG' and image.mode not in ('RGBA', 'LA', 'P', 'RGB', 'L'):
                    image = image.convert('RGBA')
                
                elif output_format == 'GIF':
                    if image.mode != 'P':
                        image = image.convert('P', palette=Image.ADAPTIVE, colors=256)
                
                elif output_format == 'ICO':
                    # ICO format requires specific sizes
                    sizes = options.get('sizes', [(16, 16), (32, 32), (48, 48), (64, 64)])
                    if not sizes:  # Handle empty sizes list
                        sizes = [(16, 16), (32, 32), (48, 48)]  # Default sizes
                    if image.size not in sizes:
                        # Resize to largest size if not already appropriate
                        target_size = max(sizes, key=lambda x: x[0])
                        image = image.resize(target_size, Image.Resampling.LANCZOS)
                
                # Generate output path if not provided
                if output_path is None:
                    input_file = Path(input_path)
                    extension = self.output_formats[output_format][0]
                    output_path = input_file.with_suffix(extension)
                
                # Get format-specific save options
                default_options = self.output_formats[output_format][1].copy()
                default_options.update(options)
                
                # Save image
                if output_format == 'ICO':
                    sizes = default_options.get('sizes', [(16, 16), (32, 32), (48, 48)])
                    if not sizes:  # Handle empty sizes list
                        sizes = [(16, 16), (32, 32), (48, 48)]  # Default sizes
                    image.save(output_path, format='ICO', sizes=sizes)
                else:
                    image.save(output_path, format=output_format, **default_options)
                
                return True, f"Converted: {os.path.basename(input_path)} -> {os.path.basename(output_path)}"
                
        except Exception as e:
            return False, f"Error converting {os.path.basename(input_path)}: {str(e)}"
    
    def batch_convert(self, input_folder, output_folder=None, output_format='JPEG', progress_callback=None, **options):
        """
        Batch convert images in a folder
        
        Args:
            input_folder: Folder containing images
            output_folder: Output folder (if None, uses input folder)
            output_format: Target format
            progress_callback: Function to call with progress updates
            **options: Format-specific options
        """
        if output_folder is None:
            output_folder = input_folder
            
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Find all image files
        image_files = []
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if self.is_supported_format(file):
                    image_files.append(os.path.join(root, file))
        
        results = []
        total_files = len(image_files)
        
        for i, image_file in enumerate(image_files):
            if progress_callback:
                progress_callback(i, total_files, os.path.basename(image_file))
            
            # Generate output path maintaining folder structure
            rel_path = os.path.relpath(image_file, input_folder)
            output_path = os.path.join(output_folder, rel_path)
            extension = self.output_formats[output_format][0]
            output_path = Path(output_path).with_suffix(extension)
            
            # Create output subdirectory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            success, message = self.convert_single_image(image_file, str(output_path), output_format, **options)
            results.append((success, message))
        
        return results

class ImageConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Format Converter")
        self.root.geometry("650x550")
        
        self.converter = ImageConverter()
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
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)
        
        # Options frame
        self.options_frame = ttk.LabelFrame(main_frame, text="Format Options", padding="5")
        self.options_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        self.setup_format_options()
        
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
        self.results_text = tk.Text(main_frame, height=8, width=70)
        self.results_text.grid(row=8, column=0, columnspan=4, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=8, column=4, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
    
    def setup_format_options(self):
        # Clear existing options
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        format_name = self.format_var.get()
        
        if format_name in ['JPEG', 'WEBP']:
            # Quality slider
            ttk.Label(self.options_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W, padx=5)
            self.quality_var = tk.IntVar(value=95)
            quality_scale = ttk.Scale(self.options_frame, from_=1, to=100, variable=self.quality_var, orient=tk.HORIZONTAL)
            quality_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
            self.quality_label = ttk.Label(self.options_frame, text="95")
            self.quality_label.grid(row=0, column=2, sticky=tk.W)
            quality_scale.configure(command=self.update_quality_label)
            
        elif format_name == 'ICO':
            # ICO sizes
            ttk.Label(self.options_frame, text="ICO Sizes:").grid(row=0, column=0, sticky=tk.W, padx=5)
            self.ico_16_var = tk.BooleanVar(value=True)
            self.ico_32_var = tk.BooleanVar(value=True)
            self.ico_48_var = tk.BooleanVar(value=True)
            self.ico_64_var = tk.BooleanVar(value=False)
            
            ttk.Checkbutton(self.options_frame, text="16x16", variable=self.ico_16_var).grid(row=0, column=1, sticky=tk.W)
            ttk.Checkbutton(self.options_frame, text="32x32", variable=self.ico_32_var).grid(row=0, column=2, sticky=tk.W)
            ttk.Checkbutton(self.options_frame, text="48x48", variable=self.ico_48_var).grid(row=0, column=3, sticky=tk.W)
            ttk.Checkbutton(self.options_frame, text="64x64", variable=self.ico_64_var).grid(row=0, column=4, sticky=tk.W)
        
        self.options_frame.columnconfigure(1, weight=1)
    
    def on_format_change(self, event):
        self.setup_format_options()
    
    def update_quality_label(self, value):
        if hasattr(self, 'quality_label'):
            self.quality_label.config(text=str(int(float(value))))
    
    def browse_input(self):
        if self.mode_var.get() == "single":
            filename = filedialog.askopenfilename(
                title="Select image file",
                filetypes=[("Image files", " ".join(f"*{ext}" for ext in self.converter.input_formats)),
                          ("All files", "*.*")]
            )
            if filename:
                self.input_path_var.set(filename)
        else:
            folder = filedialog.askdirectory(title="Select folder containing images")
            if folder:
                self.input_path_var.set(folder)
    
    def browse_output(self):
        if self.mode_var.get() == "single":
            extension = self.converter.output_formats[self.format_var.get()][0]
            filename = filedialog.asksaveasfilename(
                title="Save converted file as",
                defaultextension=extension,
                filetypes=[(f"{self.format_var.get()} files", f"*{extension}")]
            )
            if filename:
                self.output_path_var.set(filename)
        else:
            folder = filedialog.askdirectory(title="Select output folder")
            if folder:
                self.output_path_var.set(folder)
    
    def get_format_options(self):
        """Get current format-specific options"""
        options = {}
        format_name = self.format_var.get()
        
        if format_name in ['JPEG', 'WEBP'] and hasattr(self, 'quality_var'):
            options['quality'] = self.quality_var.get()
        
        elif format_name == 'ICO' and hasattr(self, 'ico_16_var'):
            sizes = []
            if self.ico_16_var.get(): sizes.append((16, 16))
            if self.ico_32_var.get(): sizes.append((32, 32))
            if self.ico_48_var.get(): sizes.append((48, 48))
            if self.ico_64_var.get(): sizes.append((64, 64))
            if sizes:
                options['sizes'] = sizes
        
        return options
    
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
            
            options = self.get_format_options()
            
            if self.mode_var.get() == "single":
                # Single file conversion
                input_path = self.input_path_var.get()
                output_path = self.output_path_var.get() if self.output_path_var.get() else None
                
                self.status_var.set("Converting...")
                success, message = self.converter.convert_single_image(
                    input_path, output_path, self.format_var.get(), **options
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
                    self.progress_callback, **options
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
        converter = ImageConverter()
        
        if len(sys.argv) >= 3:
            input_file = sys.argv[1]
            output_format = sys.argv[2].upper()
            output_file = sys.argv[3] if len(sys.argv) > 3 else None
            
            success, message = converter.convert_single_image(input_file, output_file, output_format)
            print(message)
        else:
            print("Usage: python image_converter.py input_file output_format [output_file]")
            print("Available formats: JPEG, PNG, TIFF, WEBP, BMP, GIF, ICO")
    else:
        # GUI mode
        root = tk.Tk()
        app = ImageConverterGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
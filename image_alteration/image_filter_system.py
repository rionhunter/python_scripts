#!/usr/bin/env python3
"""
Image Filter System
Create, save, and apply custom filters to images
Supports batch processing and filter presets
"""

import sys
import os
import json
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
import threading
from pathlib import Path
import numpy as np
from PIL import ImageDraw

class ImageFilterSystem:
    def __init__(self):
        self.filters_dir = os.path.join(os.path.dirname(__file__), "filters")
        os.makedirs(self.filters_dir, exist_ok=True)
        
        # Built-in filter presets
        self.builtin_filters = {
            "Blur": {"type": "blur", "radius": 2},
            "Sharpen": {"type": "enhance", "sharpness": 1.5},
            "High Contrast": {"type": "enhance", "contrast": 1.8},
            "Bright": {"type": "enhance", "brightness": 1.3},
            "Saturated": {"type": "enhance", "color": 1.4},
            "Grayscale": {"type": "grayscale"},
            "Sepia": {"type": "sepia"},
            "Vintage": {"type": "composite", "filters": [
                {"type": "enhance", "contrast": 0.9},
                {"type": "enhance", "brightness": 1.1},
                {"type": "sepia"},
                {"type": "vignette", "strength": 0.3}
            ]},
            "Cool Tone": {"type": "color_balance", "red": 0.9, "green": 1.0, "blue": 1.2},
            "Warm Tone": {"type": "color_balance", "red": 1.2, "green": 1.1, "blue": 0.8},
            "Edge Enhance": {"type": "filter", "filter": "EDGE_ENHANCE"},
            "Emboss": {"type": "filter", "filter": "EMBOSS"},
            "Find Edges": {"type": "filter", "filter": "FIND_EDGES"}
        }
    
    def apply_filter(self, image, filter_config):
        """Apply a single filter to an image"""
        if filter_config["type"] == "blur":
            return image.filter(ImageFilter.GaussianBlur(radius=filter_config.get("radius", 2)))
        
        elif filter_config["type"] == "enhance":
            result = image
            if "brightness" in filter_config:
                enhancer = ImageEnhance.Brightness(result)
                result = enhancer.enhance(filter_config["brightness"])
            if "contrast" in filter_config:
                enhancer = ImageEnhance.Contrast(result)
                result = enhancer.enhance(filter_config["contrast"])
            if "color" in filter_config:
                enhancer = ImageEnhance.Color(result)
                result = enhancer.enhance(filter_config["color"])
            if "sharpness" in filter_config:
                enhancer = ImageEnhance.Sharpness(result)
                result = enhancer.enhance(filter_config["sharpness"])
            return result
        
        elif filter_config["type"] == "grayscale":
            return ImageOps.grayscale(image).convert("RGB")
        
        elif filter_config["type"] == "sepia":
            grayscale = ImageOps.grayscale(image)
            sepia = ImageOps.colorize(grayscale, "#704214", "#C0A882")
            return sepia
        
        elif filter_config["type"] == "color_balance":
            # Apply color balance by adjusting RGB channels
            r, g, b = image.split()
            if image.mode == "RGBA":
                r, g, b, a = image.split()
            
            # Apply multipliers
            r_mult = filter_config.get("red", 1.0)
            g_mult = filter_config.get("green", 1.0)
            b_mult = filter_config.get("blue", 1.0)
            
            r = r.point(lambda x: min(255, int(x * r_mult)))
            g = g.point(lambda x: min(255, int(x * g_mult)))
            b = b.point(lambda x: min(255, int(x * b_mult)))
            
            if image.mode == "RGBA":
                return Image.merge("RGBA", (r, g, b, a))
            else:
                return Image.merge("RGB", (r, g, b))
        
        elif filter_config["type"] == "filter":
            filter_name = filter_config.get("filter", "BLUR")
            pil_filter = getattr(ImageFilter, filter_name, ImageFilter.BLUR)
            return image.filter(pil_filter)
        
        elif filter_config["type"] == "vignette":
            return self.apply_vignette(image, filter_config.get("strength", 0.5))
        
        elif filter_config["type"] == "composite":
            # Apply multiple filters in sequence
            result = image
            for sub_filter in filter_config.get("filters", []):
                result = self.apply_filter(result, sub_filter)
            return result
        
        return image
    
    def apply_vignette(self, image, strength=0.5):
        """Apply a vignette effect"""
        width, height = image.size
        
        # Create a mask for vignette
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        
        # Calculate vignette parameters
        center_x, center_y = width // 2, height // 2
        max_radius = min(center_x, center_y)
        
        # Create radial gradient
        for y in range(height):
            for x in range(width):
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                if distance <= max_radius:
                    # Normalize distance and apply vignette curve
                    normalized = distance / max_radius
                    vignette_value = int(255 * (1 - normalized * strength))
                    mask.putpixel((x, y), max(0, min(255, vignette_value)))
                else:
                    mask.putpixel((x, y), int(255 * (1 - strength)))
        
        # Apply vignette by blending with black
        black_image = Image.new('RGB', image.size, (0, 0, 0))
        
        if image.mode == 'RGBA':
            # Handle alpha channel
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1])
            result = Image.composite(rgb_image, black_image, mask)
            
            # Add alpha channel back
            result.putalpha(image.split()[-1])
            return result
        else:
            return Image.composite(image, black_image, mask)
    
    def save_filter(self, name, filter_config):
        """Save a filter configuration to file"""
        filepath = os.path.join(self.filters_dir, f"{name}.json")
        with open(filepath, 'w') as f:
            json.dump(filter_config, f, indent=2)
    
    def load_filter(self, name):
        """Load a filter configuration from file"""
        filepath = os.path.join(self.filters_dir, f"{name}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def list_saved_filters(self):
        """List all saved filter configurations"""
        filters = []
        if os.path.exists(self.filters_dir):
            for filename in os.listdir(self.filters_dir):
                if filename.endswith('.json'):
                    filters.append(filename[:-5])  # Remove .json extension
        return filters
    
    def get_all_filters(self):
        """Get all available filters (built-in + saved)"""
        all_filters = self.builtin_filters.copy()
        for filter_name in self.list_saved_filters():
            filter_config = self.load_filter(filter_name)
            if filter_config:
                all_filters[filter_name] = filter_config
        return all_filters
    
    def apply_filter_to_image(self, input_path, output_path, filter_name_or_config):
        """Apply a filter to a single image"""
        try:
            with Image.open(input_path) as image:
                if isinstance(filter_name_or_config, str):
                    # Get filter by name
                    all_filters = self.get_all_filters()
                    if filter_name_or_config not in all_filters:
                        return False, f"Filter '{filter_name_or_config}' not found"
                    filter_config = all_filters[filter_name_or_config]
                else:
                    # Use provided filter configuration
                    filter_config = filter_name_or_config
                
                # Apply filter
                filtered_image = self.apply_filter(image, filter_config)
                
                # Save result
                filtered_image.save(output_path, quality=95, optimize=True)
                
                filter_name = filter_name_or_config if isinstance(filter_name_or_config, str) else "custom"
                return True, f"Applied '{filter_name}' to {os.path.basename(input_path)}"
                
        except Exception as e:
            return False, f"Error processing {os.path.basename(input_path)}: {str(e)}"
    
    def batch_apply_filter(self, input_folder, output_folder, filter_name_or_config, progress_callback=None):
        """Apply a filter to all images in a folder"""
        os.makedirs(output_folder, exist_ok=True)
        
        # Find all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.webp', '.bmp']
        image_files = []
        
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(os.path.join(root, file))
        
        results = []
        total_files = len(image_files)
        
        for i, image_file in enumerate(image_files):
            if progress_callback:
                progress_callback(i, total_files, os.path.basename(image_file))
            
            # Generate output path
            rel_path = os.path.relpath(image_file, input_folder)
            output_path = os.path.join(output_folder, rel_path)
            
            # Create output subdirectory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Apply filter
            success, message = self.apply_filter_to_image(image_file, output_path, filter_name_or_config)
            results.append((success, message))
        
        return results

class FilterEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Filter System")
        self.root.geometry("800x700")
        
        self.filter_system = ImageFilterSystem()
        self.current_filter = {"type": "enhance", "brightness": 1.0, "contrast": 1.0, "color": 1.0, "sharpness": 1.0}
        self.preview_image = None
        self.original_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Filter Editor Tab
        self.editor_frame = ttk.Frame(notebook)
        notebook.add(self.editor_frame, text="Filter Editor")
        self.setup_editor_tab()
        
        # Batch Processing Tab
        self.batch_frame = ttk.Frame(notebook)
        notebook.add(self.batch_frame, text="Batch Processing")
        self.setup_batch_tab()
    
    def setup_editor_tab(self):
        # Left panel - controls
        left_panel = ttk.Frame(self.editor_frame)
        left_panel.pack(side='left', fill='y', padx=10, pady=10)
        
        # Image selection
        ttk.Label(left_panel, text="Select Image:").pack(anchor='w', pady=5)
        ttk.Button(left_panel, text="Browse Image", command=self.browse_image).pack(fill='x', pady=5)
        
        # Filter type selection
        ttk.Label(left_panel, text="Filter Type:").pack(anchor='w', pady=(20, 5))
        self.filter_type_var = tk.StringVar(value="enhance")
        filter_types = ["enhance", "blur", "grayscale", "sepia", "color_balance", "filter", "vignette"]
        filter_combo = ttk.Combobox(left_panel, textvariable=self.filter_type_var, values=filter_types, state="readonly")
        filter_combo.pack(fill='x', pady=5)
        filter_combo.bind('<<ComboboxSelected>>', self.on_filter_type_change)
        
        # Filter parameters frame
        self.params_frame = ttk.LabelFrame(left_panel, text="Parameters", padding="10")
        self.params_frame.pack(fill='x', pady=10)
        
        # Preset filters
        ttk.Label(left_panel, text="Presets:").pack(anchor='w', pady=(20, 5))
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(left_panel, textvariable=self.preset_var, state="readonly")
        self.preset_combo.pack(fill='x', pady=5)
        self.preset_combo.bind('<<ComboboxSelected>>', self.load_preset)
        
        # Update preset list
        self.update_preset_list(self.preset_combo)
        
        # Control buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="Preview", command=self.preview_filter).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Apply", command=self.apply_filter).pack(side='left', padx=5)
        
        # Save filter
        save_frame = ttk.Frame(left_panel)
        save_frame.pack(fill='x', pady=10)
        
        ttk.Label(save_frame, text="Save as:").pack(anchor='w')
        self.save_name_var = tk.StringVar()
        ttk.Entry(save_frame, textvariable=self.save_name_var).pack(fill='x', pady=5)
        ttk.Button(save_frame, text="Save Filter", command=self.save_filter).pack(fill='x')
        
        # Right panel - image preview
        right_panel = ttk.Frame(self.editor_frame)
        right_panel.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # Image display
        self.image_frame = ttk.LabelFrame(right_panel, text="Preview", padding="10")
        self.image_frame.pack(fill='both', expand=True)
        
        self.image_label = ttk.Label(self.image_frame, text="No image selected")
        self.image_label.pack(expand=True)
        
        # Setup initial parameters
        self.setup_filter_params()
    
    def setup_batch_tab(self):
        # Batch processing controls
        main_frame = ttk.Frame(self.batch_frame, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Input folder
        ttk.Label(main_frame, text="Input Folder:").grid(row=0, column=0, sticky='w', pady=5)
        self.batch_input_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.batch_input_var, width=50).grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_batch_input).grid(row=0, column=2, padx=5)
        
        # Output folder
        ttk.Label(main_frame, text="Output Folder:").grid(row=1, column=0, sticky='w', pady=5)
        self.batch_output_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.batch_output_var, width=50).grid(row=1, column=1, sticky='ew', padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_batch_output).grid(row=1, column=2, padx=5)
        
        # Filter selection
        ttk.Label(main_frame, text="Filter:").grid(row=2, column=0, sticky='w', pady=5)
        self.batch_filter_var = tk.StringVar()
        self.batch_filter_combo = ttk.Combobox(main_frame, textvariable=self.batch_filter_var, state="readonly")
        self.batch_filter_combo.grid(row=2, column=1, sticky='ew', padx=5)
        
        # Update filter list for batch processing
        self.update_batch_filter_list()
        
        # Process button
        ttk.Button(main_frame, text="Process All Images", command=self.start_batch_processing).grid(row=3, column=1, pady=20)
        
        # Progress bar
        self.batch_progress_var = tk.DoubleVar()
        self.batch_progress_bar = ttk.Progressbar(main_frame, variable=self.batch_progress_var, maximum=100)
        self.batch_progress_bar.grid(row=4, column=0, columnspan=3, sticky='ew', pady=5)
        
        # Status
        self.batch_status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.batch_status_var).grid(row=5, column=0, columnspan=3, pady=5)
        
        # Results
        self.batch_results_text = tk.Text(main_frame, height=15, width=70)
        self.batch_results_text.grid(row=6, column=0, columnspan=3, pady=10, sticky='nsew')
        
        # Scrollbar
        batch_scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.batch_results_text.yview)
        batch_scrollbar.grid(row=6, column=3, sticky='ns')
        self.batch_results_text.configure(yscrollcommand=batch_scrollbar.set)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
    
    def setup_filter_params(self):
        # Clear existing parameters
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        filter_type = self.filter_type_var.get()
        
        if filter_type == "enhance":
            # Brightness
            ttk.Label(self.params_frame, text="Brightness:").grid(row=0, column=0, sticky='w')
            self.brightness_var = tk.DoubleVar(value=1.0)
            brightness_scale = ttk.Scale(self.params_frame, from_=0.1, to=3.0, variable=self.brightness_var, orient='horizontal')
            brightness_scale.grid(row=0, column=1, sticky='ew')
            
            # Contrast
            ttk.Label(self.params_frame, text="Contrast:").grid(row=1, column=0, sticky='w')
            self.contrast_var = tk.DoubleVar(value=1.0)
            contrast_scale = ttk.Scale(self.params_frame, from_=0.1, to=3.0, variable=self.contrast_var, orient='horizontal')
            contrast_scale.grid(row=1, column=1, sticky='ew')
            
            # Color saturation
            ttk.Label(self.params_frame, text="Saturation:").grid(row=2, column=0, sticky='w')
            self.saturation_var = tk.DoubleVar(value=1.0)
            saturation_scale = ttk.Scale(self.params_frame, from_=0.0, to=3.0, variable=self.saturation_var, orient='horizontal')
            saturation_scale.grid(row=2, column=1, sticky='ew')
            
            # Sharpness
            ttk.Label(self.params_frame, text="Sharpness:").grid(row=3, column=0, sticky='w')
            self.sharpness_var = tk.DoubleVar(value=1.0)
            sharpness_scale = ttk.Scale(self.params_frame, from_=0.0, to=3.0, variable=self.sharpness_var, orient='horizontal')
            sharpness_scale.grid(row=3, column=1, sticky='ew')
            
        elif filter_type == "blur":
            ttk.Label(self.params_frame, text="Radius:").grid(row=0, column=0, sticky='w')
            self.blur_radius_var = tk.DoubleVar(value=2.0)
            blur_scale = ttk.Scale(self.params_frame, from_=0.1, to=10.0, variable=self.blur_radius_var, orient='horizontal')
            blur_scale.grid(row=0, column=1, sticky='ew')
            
        elif filter_type == "color_balance":
            ttk.Label(self.params_frame, text="Red:").grid(row=0, column=0, sticky='w')
            self.red_var = tk.DoubleVar(value=1.0)
            red_scale = ttk.Scale(self.params_frame, from_=0.1, to=2.0, variable=self.red_var, orient='horizontal')
            red_scale.grid(row=0, column=1, sticky='ew')
            
            ttk.Label(self.params_frame, text="Green:").grid(row=1, column=0, sticky='w')
            self.green_var = tk.DoubleVar(value=1.0)
            green_scale = ttk.Scale(self.params_frame, from_=0.1, to=2.0, variable=self.green_var, orient='horizontal')
            green_scale.grid(row=1, column=1, sticky='ew')
            
            ttk.Label(self.params_frame, text="Blue:").grid(row=2, column=0, sticky='w')
            self.blue_var = tk.DoubleVar(value=1.0)
            blue_scale = ttk.Scale(self.params_frame, from_=0.1, to=2.0, variable=self.blue_var, orient='horizontal')
            blue_scale.grid(row=2, column=1, sticky='ew')
            
        elif filter_type == "vignette":
            ttk.Label(self.params_frame, text="Strength:").grid(row=0, column=0, sticky='w')
            self.vignette_strength_var = tk.DoubleVar(value=0.5)
            vignette_scale = ttk.Scale(self.params_frame, from_=0.0, to=1.0, variable=self.vignette_strength_var, orient='horizontal')
            vignette_scale.grid(row=0, column=1, sticky='ew')
            
        elif filter_type == "filter":
            ttk.Label(self.params_frame, text="Filter:").grid(row=0, column=0, sticky='w')
            self.pil_filter_var = tk.StringVar(value="BLUR")
            pil_filters = ["BLUR", "CONTOUR", "DETAIL", "EDGE_ENHANCE", "EDGE_ENHANCE_MORE", 
                          "EMBOSS", "FIND_EDGES", "SHARPEN", "SMOOTH", "SMOOTH_MORE"]
            filter_combo = ttk.Combobox(self.params_frame, textvariable=self.pil_filter_var, values=pil_filters, state="readonly")
            filter_combo.grid(row=0, column=1, sticky='ew')
        
        # Configure grid weights
        self.params_frame.columnconfigure(1, weight=1)
    
    def on_filter_type_change(self, event):
        self.setup_filter_params()
    
    def update_preset_list(self, combo_widget):
        all_filters = self.filter_system.get_all_filters()
        combo_widget['values'] = list(all_filters.keys())
    
    def update_batch_filter_list(self):
        all_filters = self.filter_system.get_all_filters()
        self.batch_filter_combo['values'] = list(all_filters.keys())
    
    def browse_image(self):
        filename = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.tiff *.tif *.webp *.bmp")]
        )
        if filename:
            self.load_image(filename)
    
    def load_image(self, filepath):
        try:
            self.original_image = Image.open(filepath)
            self.show_image(self.original_image)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def show_image(self, image):
        # Resize image for display
        display_size = (400, 300)
        image_copy = image.copy()
        image_copy.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        from PIL import ImageTk
        photo = ImageTk.PhotoImage(image_copy)
        
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo  # Keep a reference
    
    def get_current_filter_config(self):
        filter_type = self.filter_type_var.get()
        config = {"type": filter_type}
        
        if filter_type == "enhance":
            if hasattr(self, 'brightness_var'):
                config["brightness"] = self.brightness_var.get()
            if hasattr(self, 'contrast_var'):
                config["contrast"] = self.contrast_var.get()
            if hasattr(self, 'saturation_var'):
                config["color"] = self.saturation_var.get()
            if hasattr(self, 'sharpness_var'):
                config["sharpness"] = self.sharpness_var.get()
        elif filter_type == "blur":
            if hasattr(self, 'blur_radius_var'):
                config["radius"] = self.blur_radius_var.get()
        elif filter_type == "color_balance":
            if hasattr(self, 'red_var'):
                config["red"] = self.red_var.get()
            if hasattr(self, 'green_var'):
                config["green"] = self.green_var.get()
            if hasattr(self, 'blue_var'):
                config["blue"] = self.blue_var.get()
        elif filter_type == "vignette":
            if hasattr(self, 'vignette_strength_var'):
                config["strength"] = self.vignette_strength_var.get()
        elif filter_type == "filter":
            if hasattr(self, 'pil_filter_var'):
                config["filter"] = self.pil_filter_var.get()
        
        return config
    
    def preview_filter(self):
        if not self.original_image:
            messagebox.showwarning("Warning", "Please select an image first")
            return
        
        try:
            filter_config = self.get_current_filter_config()
            filtered_image = self.filter_system.apply_filter(self.original_image, filter_config)
            self.show_image(filtered_image)
            self.preview_image = filtered_image
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {str(e)}")
    
    def apply_filter(self):
        if not self.preview_image:
            messagebox.showwarning("Warning", "Please preview the filter first")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save filtered image",
            defaultextension=".jpg",
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.preview_image.save(filename, quality=95, optimize=True)
                messagebox.showinfo("Success", f"Image saved as {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def save_filter(self):
        name = self.save_name_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a filter name")
            return
        
        try:
            filter_config = self.get_current_filter_config()
            self.filter_system.save_filter(name, filter_config)
            messagebox.showinfo("Success", f"Filter '{name}' saved successfully")
            
            # Update preset lists
            self.update_preset_list(self.preset_combo)
            self.update_batch_filter_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save filter: {str(e)}")
    
    def load_preset(self, event):
        preset_name = self.preset_var.get()
        if not preset_name:
            return
        
        try:
            all_filters = self.filter_system.get_all_filters()
            if preset_name in all_filters:
                filter_config = all_filters[preset_name]
                self.load_filter_config(filter_config)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preset: {str(e)}")
    
    def load_filter_config(self, config):
        # Set filter type
        self.filter_type_var.set(config.get("type", "enhance"))
        self.setup_filter_params()
        
        # Set parameters based on filter type
        filter_type = config.get("type")
        
        if filter_type == "enhance":
            if hasattr(self, 'brightness_var') and "brightness" in config:
                self.brightness_var.set(config["brightness"])
            if hasattr(self, 'contrast_var') and "contrast" in config:
                self.contrast_var.set(config["contrast"])
            if hasattr(self, 'saturation_var') and "color" in config:
                self.saturation_var.set(config["color"])
            if hasattr(self, 'sharpness_var') and "sharpness" in config:
                self.sharpness_var.set(config["sharpness"])
        elif filter_type == "blur":
            if hasattr(self, 'blur_radius_var') and "radius" in config:
                self.blur_radius_var.set(config["radius"])
        elif filter_type == "color_balance":
            if hasattr(self, 'red_var') and "red" in config:
                self.red_var.set(config["red"])
            if hasattr(self, 'green_var') and "green" in config:
                self.green_var.set(config["green"])
            if hasattr(self, 'blue_var') and "blue" in config:
                self.blue_var.set(config["blue"])
        elif filter_type == "vignette":
            if hasattr(self, 'vignette_strength_var') and "strength" in config:
                self.vignette_strength_var.set(config["strength"])
        elif filter_type == "filter":
            if hasattr(self, 'pil_filter_var') and "filter" in config:
                self.pil_filter_var.set(config["filter"])
    
    def browse_batch_input(self):
        folder = filedialog.askdirectory(title="Select input folder")
        if folder:
            self.batch_input_var.set(folder)
    
    def browse_batch_output(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.batch_output_var.set(folder)
    
    def batch_progress_callback(self, current, total, filename):
        progress = (current / total) * 100
        self.batch_progress_var.set(progress)
        self.batch_status_var.set(f"Processing: {filename} ({current+1}/{total})")
        self.root.update_idletasks()
    
    def start_batch_processing(self):
        if not self.batch_input_var.get():
            messagebox.showerror("Error", "Please select input folder")
            return
        if not self.batch_output_var.get():
            messagebox.showerror("Error", "Please select output folder")
            return
        if not self.batch_filter_var.get():
            messagebox.showerror("Error", "Please select a filter")
            return
        
        # Start batch processing in separate thread
        thread = threading.Thread(target=self.process_batch)
        thread.daemon = True
        thread.start()
    
    def process_batch(self):
        try:
            self.batch_results_text.delete(1.0, tk.END)
            self.batch_progress_var.set(0)
            
            results = self.filter_system.batch_apply_filter(
                self.batch_input_var.get(),
                self.batch_output_var.get(),
                self.batch_filter_var.get(),
                self.batch_progress_callback
            )
            
            # Display results
            success_count = sum(1 for success, _ in results if success)
            total_count = len(results)
            
            self.batch_results_text.insert(tk.END, f"Batch processing complete: {success_count}/{total_count} successful\n\n")
            
            for success, message in results:
                self.batch_results_text.insert(tk.END, f"{'✓' if success else '✗'} {message}\n")
            
            self.batch_progress_var.set(100)
            self.batch_status_var.set(f"Complete: {success_count}/{total_count} successful")
            
        except Exception as e:
            messagebox.showerror("Error", f"Batch processing failed: {str(e)}")
            self.batch_status_var.set("Error")

def main():
    root = tk.Tk()
    app = FilterEditorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
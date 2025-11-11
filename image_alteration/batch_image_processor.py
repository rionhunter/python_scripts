#!/usr/bin/env python3
"""
Batch Image Processor
Central script for batch processing images with conversion and filtering
Supports command-line and GUI modes
"""

import sys
import os
import json
import argparse
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

# Import our custom modules
try:
    from raw_converter import RawConverter
    from image_converter import ImageConverter
    from image_filter_system import ImageFilterSystem
except ImportError:
    print("Error: Required modules not found. Make sure raw_converter.py, image_converter.py, and image_filter_system.py are in the same directory.")
    sys.exit(1)

class BatchImageProcessor:
    def __init__(self):
        self.raw_converter = RawConverter()
        self.image_converter = ImageConverter()
        self.filter_system = ImageFilterSystem()
        
    def process_batch(self, input_folder, output_folder, operations, progress_callback=None):
        """
        Process a batch of images with multiple operations
        
        Args:
            input_folder: Input directory
            output_folder: Output directory
            operations: List of operation dictionaries
            progress_callback: Progress callback function
        
        Operations format:
        [
            {"type": "convert_raw", "format": "JPEG", "quality": 95},
            {"type": "convert_format", "format": "PNG"},
            {"type": "apply_filter", "filter": "Vintage"}
        ]
        """
        os.makedirs(output_folder, exist_ok=True)
        
        # Find all supported files
        all_files = []
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if (self.raw_converter.is_raw_file(file_path) or 
                    self.image_converter.is_supported_format(file_path)):
                    all_files.append(file_path)
        
        results = []
        total_files = len(all_files)
        
        for i, file_path in enumerate(all_files):
            if progress_callback:
                progress_callback(i, total_files, os.path.basename(file_path))
            
            # Generate output path
            rel_path = os.path.relpath(file_path, input_folder)
            current_output = os.path.join(output_folder, rel_path)
            os.makedirs(os.path.dirname(current_output), exist_ok=True)
            
            # Process through operations chain
            current_file = file_path
            temp_files = []
            final_output_path = current_output  # Track the final output path
            
            try:
                for op_index, operation in enumerate(operations):
                    op_type = operation.get("type")
                    
                    if op_type == "convert_raw" and self.raw_converter.is_raw_file(current_file):
                        # Convert RAW to specified format
                        format_name = operation.get("format", "JPEG")
                        quality = operation.get("quality", 95)
                        
                        # Update final output path extension
                        final_output_path = str(Path(current_output).with_suffix(
                            self.raw_converter.output_formats[format_name]
                        ))
                        
                        if op_index == len(operations) - 1:
                            # Last operation, use final output path
                            next_file = final_output_path
                        else:
                            # Intermediate file
                            next_file = str(Path(current_output).with_suffix(
                                self.raw_converter.output_formats[format_name]
                            )) + f"_temp_{op_index}"
                            temp_files.append(next_file)
                        
                        success, message = self.raw_converter.convert_single_raw(
                            current_file, str(next_file), format_name, quality
                        )
                        
                        if not success:
                            results.append((False, message))
                            break
                        
                        current_file = str(next_file)
                    
                    elif op_type == "convert_format":
                        # Convert between image formats
                        format_name = operation.get("format", "JPEG")
                        
                        # Update final output path extension
                        final_output_path = str(Path(current_output).with_suffix(
                            self.image_converter.output_formats[format_name][0]
                        ))
                        
                        if op_index == len(operations) - 1:
                            # Last operation, use final output path
                            next_file = final_output_path
                        else:
                            # Intermediate file
                            next_file = str(Path(current_output).with_suffix(
                                self.image_converter.output_formats[format_name][0]
                            )) + f"_temp_{op_index}"
                            temp_files.append(next_file)
                        
                        options = {}
                        if "quality" in operation:
                            options["quality"] = operation["quality"]
                        
                        success, message = self.image_converter.convert_single_image(
                            current_file, str(next_file), format_name, **options
                        )
                        
                        if not success:
                            results.append((False, message))
                            break
                        
                        current_file = str(next_file)
                    
                    elif op_type == "apply_filter":
                        # Apply image filter
                        filter_name = operation.get("filter")
                        
                        if op_index == len(operations) - 1:
                            # Last operation, use final output path (keep extension from previous operations)
                            next_file = final_output_path
                        else:
                            # Intermediate file (keep current extension)
                            current_ext = Path(current_file).suffix
                            next_file = str(Path(current_output).with_suffix(current_ext)) + f"_temp_{op_index}"
                            temp_files.append(next_file)
                        
                        success, message = self.filter_system.apply_filter_to_image(
                            current_file, next_file, filter_name
                        )
                        
                        if not success:
                            results.append((False, message))
                            break
                        
                        current_file = next_file
                
                else:
                    # All operations completed successfully
                    results.append((True, f"Processed: {os.path.basename(file_path)}"))
                
            except Exception as e:
                results.append((False, f"Error processing {os.path.basename(file_path)}: {str(e)}"))
            
            finally:
                # Clean up temporary files
                for temp_file in temp_files:
                    try:
                        if os.path.exists(temp_file) and temp_file != current_file:
                            os.remove(temp_file)
                    except:
                        pass
        
        return results

class BatchProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Image Processor")
        self.root.geometry("800x700")
        
        self.processor = BatchImageProcessor()
        self.operations = []
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Input/Output selection
        io_frame = ttk.LabelFrame(main_frame, text="Input/Output", padding="10")
        io_frame.pack(fill='x', pady=10)
        
        # Input folder
        ttk.Label(io_frame, text="Input Folder:").grid(row=0, column=0, sticky='w', pady=5)
        self.input_var = tk.StringVar()
        ttk.Entry(io_frame, textvariable=self.input_var, width=50).grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Button(io_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5)
        
        # Output folder
        ttk.Label(io_frame, text="Output Folder:").grid(row=1, column=0, sticky='w', pady=5)
        self.output_var = tk.StringVar()
        ttk.Entry(io_frame, textvariable=self.output_var, width=50).grid(row=1, column=1, sticky='ew', padx=5)
        ttk.Button(io_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, padx=5)
        
        io_frame.columnconfigure(1, weight=1)
        
        # Operations configuration
        ops_frame = ttk.LabelFrame(main_frame, text="Processing Operations", padding="10")
        ops_frame.pack(fill='both', expand=True, pady=10)
        
        # Operations list
        list_frame = ttk.Frame(ops_frame)
        list_frame.pack(fill='both', expand=True)
        
        self.ops_listbox = tk.Listbox(list_frame, height=8)
        self.ops_listbox.pack(side='left', fill='both', expand=True)
        
        ops_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.ops_listbox.yview)
        ops_scrollbar.pack(side='right', fill='y')
        self.ops_listbox.configure(yscrollcommand=ops_scrollbar.set)
        
        # Operation buttons
        ops_buttons_frame = ttk.Frame(ops_frame)
        ops_buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(ops_buttons_frame, text="Add RAW Conversion", command=self.add_raw_conversion).pack(side='left', padx=5)
        ttk.Button(ops_buttons_frame, text="Add Format Conversion", command=self.add_format_conversion).pack(side='left', padx=5)
        ttk.Button(ops_buttons_frame, text="Add Filter", command=self.add_filter).pack(side='left', padx=5)
        ttk.Button(ops_buttons_frame, text="Remove Selected", command=self.remove_operation).pack(side='left', padx=5)
        ttk.Button(ops_buttons_frame, text="Clear All", command=self.clear_operations).pack(side='left', padx=5)
        
        # Move operations
        move_frame = ttk.Frame(ops_frame)
        move_frame.pack(fill='x', pady=5)
        
        ttk.Button(move_frame, text="Move Up", command=self.move_up).pack(side='left', padx=5)
        ttk.Button(move_frame, text="Move Down", command=self.move_down).pack(side='left', padx=5)
        
        # Process button
        ttk.Button(main_frame, text="Start Processing", command=self.start_processing).pack(pady=20)
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).pack(pady=5)
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.pack(fill='both', expand=True, pady=10)
        
        self.results_text = tk.Text(results_frame, height=10)
        self.results_text.pack(fill='both', expand=True)
        
        results_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_text.yview)
        results_scrollbar.pack(side='right', fill='y')
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
    
    def browse_input(self):
        folder = filedialog.askdirectory(title="Select input folder")
        if folder:
            self.input_var.set(folder)
    
    def browse_output(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_var.set(folder)
    
    def add_raw_conversion(self):
        dialog = RawConversionDialog(self.root)
        if dialog.result:
            self.operations.append(dialog.result)
            self.update_operations_list()
    
    def add_format_conversion(self):
        dialog = FormatConversionDialog(self.root)
        if dialog.result:
            self.operations.append(dialog.result)
            self.update_operations_list()
    
    def add_filter(self):
        dialog = FilterDialog(self.root, self.processor.filter_system)
        if dialog.result:
            self.operations.append(dialog.result)
            self.update_operations_list()
    
    def remove_operation(self):
        selection = self.ops_listbox.curselection()
        if selection:
            index = selection[0]
            del self.operations[index]
            self.update_operations_list()
    
    def clear_operations(self):
        self.operations.clear()
        self.update_operations_list()
    
    def move_up(self):
        selection = self.ops_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            self.operations[index], self.operations[index-1] = self.operations[index-1], self.operations[index]
            self.update_operations_list()
            self.ops_listbox.selection_set(index-1)
    
    def move_down(self):
        selection = self.ops_listbox.curselection()
        if selection and selection[0] < len(self.operations) - 1:
            index = selection[0]
            self.operations[index], self.operations[index+1] = self.operations[index+1], self.operations[index]
            self.update_operations_list()
            self.ops_listbox.selection_set(index+1)
    
    def update_operations_list(self):
        self.ops_listbox.delete(0, tk.END)
        for i, op in enumerate(self.operations):
            if op["type"] == "convert_raw":
                desc = f"{i+1}. Convert RAW to {op.get('format', 'JPEG')} (Quality: {op.get('quality', 95)})"
            elif op["type"] == "convert_format":
                desc = f"{i+1}. Convert to {op.get('format', 'JPEG')}"
            elif op["type"] == "apply_filter":
                desc = f"{i+1}. Apply filter: {op.get('filter', 'Unknown')}"
            else:
                desc = f"{i+1}. Unknown operation"
            
            self.ops_listbox.insert(tk.END, desc)
    
    def progress_callback(self, current, total, filename):
        progress = (current / total) * 100
        self.progress_var.set(progress)
        self.status_var.set(f"Processing: {filename} ({current+1}/{total})")
        self.root.update_idletasks()
    
    def start_processing(self):
        if not self.input_var.get():
            messagebox.showerror("Error", "Please select input folder")
            return
        if not self.output_var.get():
            messagebox.showerror("Error", "Please select output folder")
            return
        if not self.operations:
            messagebox.showerror("Error", "Please add at least one operation")
            return
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.process)
        thread.daemon = True
        thread.start()
    
    def process(self):
        try:
            self.results_text.delete(1.0, tk.END)
            self.progress_var.set(0)
            
            results = self.processor.process_batch(
                self.input_var.get(),
                self.output_var.get(),
                self.operations,
                self.progress_callback
            )
            
            # Display results
            success_count = sum(1 for success, _ in results if success)
            total_count = len(results)
            
            self.results_text.insert(tk.END, f"Batch processing complete: {success_count}/{total_count} successful\n\n")
            
            for success, message in results:
                self.results_text.insert(tk.END, f"{'✓' if success else '✗'} {message}\n")
            
            self.progress_var.set(100)
            self.status_var.set(f"Complete: {success_count}/{total_count} successful")
            
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
            self.status_var.set("Error")

# Dialog classes for operation configuration
class RawConversionDialog:
    def __init__(self, parent):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title("RAW Conversion Settings")
        dialog.geometry("300x200")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Format selection
        ttk.Label(dialog, text="Output Format:").pack(pady=10)
        format_var = tk.StringVar(value="JPEG")
        format_combo = ttk.Combobox(dialog, textvariable=format_var, 
                                   values=["JPEG", "PNG", "TIFF", "WEBP"], state="readonly")
        format_combo.pack(pady=5)
        
        # Quality setting
        ttk.Label(dialog, text="Quality (JPEG/WEBP):").pack(pady=10)
        quality_var = tk.IntVar(value=95)
        quality_scale = ttk.Scale(dialog, from_=1, to=100, variable=quality_var, orient='horizontal')
        quality_scale.pack(pady=5, fill='x', padx=20)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def ok_clicked():
            self.result = {
                "type": "convert_raw",
                "format": format_var.get(),
                "quality": quality_var.get()
            }
            dialog.destroy()
        
        def cancel_clicked():
            dialog.destroy()
        
        ttk.Button(button_frame, text="OK", command=ok_clicked).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel_clicked).pack(side='left', padx=5)
        
        dialog.wait_window()

class FormatConversionDialog:
    def __init__(self, parent):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title("Format Conversion Settings")
        dialog.geometry("300x200")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Format selection
        ttk.Label(dialog, text="Output Format:").pack(pady=10)
        format_var = tk.StringVar(value="JPEG")
        format_combo = ttk.Combobox(dialog, textvariable=format_var,
                                   values=["JPEG", "PNG", "TIFF", "WEBP", "BMP", "GIF"], state="readonly")
        format_combo.pack(pady=5)
        
        # Quality setting
        ttk.Label(dialog, text="Quality (JPEG/WEBP):").pack(pady=10)
        quality_var = tk.IntVar(value=95)
        quality_scale = ttk.Scale(dialog, from_=1, to=100, variable=quality_var, orient='horizontal')
        quality_scale.pack(pady=5, fill='x', padx=20)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def ok_clicked():
            result = {
                "type": "convert_format",
                "format": format_var.get()
            }
            if format_var.get() in ["JPEG", "WEBP"]:
                result["quality"] = quality_var.get()
            self.result = result
            dialog.destroy()
        
        def cancel_clicked():
            dialog.destroy()
        
        ttk.Button(button_frame, text="OK", command=ok_clicked).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel_clicked).pack(side='left', padx=5)
        
        dialog.wait_window()

class FilterDialog:
    def __init__(self, parent, filter_system):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title("Filter Settings")
        dialog.geometry("300x150")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Filter selection
        ttk.Label(dialog, text="Select Filter:").pack(pady=10)
        filter_var = tk.StringVar()
        
        all_filters = filter_system.get_all_filters()
        filter_combo = ttk.Combobox(dialog, textvariable=filter_var,
                                   values=list(all_filters.keys()), state="readonly")
        filter_combo.pack(pady=5, fill='x', padx=20)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def ok_clicked():
            if filter_var.get():
                self.result = {
                    "type": "apply_filter",
                    "filter": filter_var.get()
                }
            dialog.destroy()
        
        def cancel_clicked():
            dialog.destroy()
        
        ttk.Button(button_frame, text="OK", command=ok_clicked).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel_clicked).pack(side='left', padx=5)
        
        dialog.wait_window()

def main():
    if len(sys.argv) > 1:
        # Command line mode
        parser = argparse.ArgumentParser(description="Batch Image Processor")
        parser.add_argument("input_folder", help="Input folder containing images")
        parser.add_argument("output_folder", help="Output folder for processed images")
        parser.add_argument("--config", help="JSON configuration file for operations")
        parser.add_argument("--convert-raw", help="Convert RAW files to format", choices=['JPEG', 'PNG', 'TIFF', 'WEBP'])
        parser.add_argument("--convert-format", help="Convert images to format", choices=['JPEG', 'PNG', 'TIFF', 'WEBP', 'BMP', 'GIF'])
        parser.add_argument("--filter", help="Apply filter by name")
        parser.add_argument("--quality", type=int, default=95, help="Quality for JPEG/WEBP (1-100)")
        
        args = parser.parse_args()
        
        # Build operations from command line arguments
        operations = []
        
        if args.convert_raw:
            operations.append({
                "type": "convert_raw",
                "format": args.convert_raw,
                "quality": args.quality
            })
        
        if args.convert_format:
            operations.append({
                "type": "convert_format",
                "format": args.convert_format,
                "quality": args.quality
            })
        
        if args.filter:
            operations.append({
                "type": "apply_filter",
                "filter": args.filter
            })
        
        if args.config:
            # Load operations from JSON config file
            with open(args.config, 'r') as f:
                config = json.load(f)
                operations = config.get("operations", [])
        
        if not operations:
            print("Error: No operations specified. Use --convert-raw, --convert-format, --filter, or --config")
            sys.exit(1)
        
        # Process batch
        processor = BatchImageProcessor()
        
        def progress_callback(current, total, filename):
            print(f"Processing: {filename} ({current+1}/{total})")
        
        print(f"Processing images from {args.input_folder} to {args.output_folder}")
        results = processor.process_batch(args.input_folder, args.output_folder, operations, progress_callback)
        
        # Display results
        success_count = sum(1 for success, _ in results if success)
        total_count = len(results)
        
        print(f"\nBatch processing complete: {success_count}/{total_count} successful")
        
        for success, message in results:
            print(f"{'✓' if success else '✗'} {message}")
    
    else:
        # GUI mode
        root = tk.Tk()
        app = BatchProcessorGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
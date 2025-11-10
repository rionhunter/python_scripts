from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def crop_transparent_image(img):
    """
    Crop excess transparent pixels from around the image.
    Returns the cropped image.
    """
    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Get the bounding box of non-transparent pixels
    bbox = img.getbbox()
    
    if bbox:
        # Crop to the bounding box
        return img.crop(bbox)
    else:
        # If image is completely transparent, return original
        return img

def create_ico_from_png(input_path, output_path, sizes=None):
    """
    Convert a PNG file to ICO format with multiple sizes.
    This version manually creates the ICO file to ensure all sizes are properly embedded.
    
    Args:
        input_path: Path to input PNG file
        output_path: Path to output ICO file
        sizes: List of sizes to include in ICO (default: [16, 20, 24, 32, 40, 48, 64, 96, 128, 256])
    """
    import struct
    import io
    
    if sizes is None:
        # Standard Windows icon sizes for optimal display
        sizes = [16, 20, 24, 32, 40, 48, 64, 96, 128, 256]
    
    try:
        # Open the PNG image
        original_img = Image.open(input_path)
        if original_img.mode != 'RGBA':
            original_img = original_img.convert('RGBA')
        
        # Crop excess transparent space
        cropped_img = crop_transparent_image(original_img)
        
        # Prepare image data for each size
        icon_data = []
        for size in sorted(sizes):
            # Resize image maintaining transparency
            resized = cropped_img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Save as PNG data (better transparency support than BMP)
            png_buffer = io.BytesIO()
            resized.save(png_buffer, format='PNG')
            png_data = png_buffer.getvalue()
            
            icon_data.append({
                'width': size if size < 256 else 0,  # 0 means 256 in ICO format
                'height': size if size < 256 else 0,
                'colors': 0,  # 0 for PNG format
                'reserved': 0,
                'planes': 1,
                'bit_count': 32,  # 32-bit RGBA
                'size': len(png_data),
                'data': png_data
            })
        
        # Write ICO file manually
        with open(output_path, 'wb') as f:
            # ICO header: Reserved(2), Type(2), Count(2)
            f.write(struct.pack('<HHH', 0, 1, len(icon_data)))
            
            # Calculate data offset
            data_offset = 6 + (16 * len(icon_data))
            
            # Write directory entries
            for icon in icon_data:
                f.write(struct.pack('<BBBBHHLL',
                    icon['width'], icon['height'], icon['colors'], icon['reserved'],
                    icon['planes'], icon['bit_count'], icon['size'], data_offset
                ))
                data_offset += icon['size']
            
            # Write image data
            for icon in icon_data:
                f.write(icon['data'])
        
        return True, f"Successfully converted to ICO with {len(icon_data)} sizes: {sizes}"
        
    except Exception as e:
        return False, f"Error converting image: {str(e)}"

def select_input_file():
    """Open file dialog to select PNG input file"""
    file_path = filedialog.askopenfilename(
        title="Select PNG file",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
    )
    if file_path:
        input_var.set(file_path)
        # Auto-generate output filename
        base_name = os.path.splitext(file_path)[0]
        output_var.set(base_name + ".ico")

def select_output_file():
    """Open file dialog to select ICO output file"""
    file_path = filedialog.asksaveasfilename(
        title="Save ICO file as",
        defaultextension=".ico",
        filetypes=[("ICO files", "*.ico"), ("All files", "*.*")]
    )
    if file_path:
        output_var.set(file_path)

def convert_file():
    """Convert the selected PNG to ICO"""
    input_path = input_var.get()
    output_path = output_var.get()
    
    if not input_path:
        messagebox.showerror("Error", "Please select an input PNG file")
        return
    
    if not output_path:
        messagebox.showerror("Error", "Please specify an output ICO file")
        return
    
    if not os.path.exists(input_path):
        messagebox.showerror("Error", "Input file does not exist")
        return
    
    # Get selected sizes
    selected_sizes = []
    for size, var in size_vars.items():
        if var.get():
            selected_sizes.append(size)
    
    if not selected_sizes:
        messagebox.showerror("Error", "Please select at least one icon size")
        return
    
    # Update status
    status_var.set("Converting...")
    root.update()
    
    # Perform conversion
    success, message = create_ico_from_png(input_path, output_path, selected_sizes)
    
    if success:
        messagebox.showinfo("Success", message)
        status_var.set("Conversion completed successfully")
    else:
        messagebox.showerror("Error", message)
        status_var.set("Conversion failed")

def preview_cropped_image():
    """Preview how the image will look after cropping"""
    input_path = input_var.get()
    
    if not input_path or not os.path.exists(input_path):
        messagebox.showerror("Error", "Please select a valid input PNG file first")
        return
    
    try:
        # Open and crop the image
        original_img = Image.open(input_path)
        cropped_img = crop_transparent_image(original_img)
        
        # Show info about the cropping
        orig_size = original_img.size
        crop_size = cropped_img.size
        
        info_text = f"Original size: {orig_size[0]}x{orig_size[1]}\n"
        info_text += f"Cropped size: {crop_size[0]}x{crop_size[1]}\n"
        info_text += f"Pixels saved: {(orig_size[0] * orig_size[1]) - (crop_size[0] * crop_size[1])}"
        
        messagebox.showinfo("Crop Preview", info_text)
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to preview image: {str(e)}")

# Create main window
root = tk.Tk()
root.title("PNG to ICO Converter")
root.geometry("600x500")
root.resizable(True, True)

# Variables
input_var = tk.StringVar()
output_var = tk.StringVar()
status_var = tk.StringVar()
status_var.set("Ready")

# Input file selection
tk.Label(root, text="Input PNG File:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
input_frame = tk.Frame(root)
input_frame.pack(fill=tk.X, padx=10, pady=5)
tk.Entry(input_frame, textvariable=input_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(input_frame, text="Browse", command=select_input_file).pack(side=tk.RIGHT, padx=(5, 0))

# Output file selection
tk.Label(root, text="Output ICO File:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
output_frame = tk.Frame(root)
output_frame.pack(fill=tk.X, padx=10, pady=5)
tk.Entry(output_frame, textvariable=output_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(output_frame, text="Browse", command=select_output_file).pack(side=tk.RIGHT, padx=(5, 0))

# Icon sizes selection
tk.Label(root, text="Select Icon Sizes to Include:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
sizes_frame = tk.Frame(root)
sizes_frame.pack(padx=10, pady=5)

# Create checkboxes for common icon sizes
size_vars = {}
common_sizes = [16, 20, 24, 32, 40, 48, 64, 96, 128, 256]
for i, size in enumerate(common_sizes):
    var = tk.BooleanVar()
    var.set(size in [16, 20, 24, 32, 40, 48, 64, 96, 128, 256])  # Default: all sizes selected
    size_vars[size] = var
    
    row = i // 5
    col = i % 5
    tk.Checkbutton(sizes_frame, text=f"{size}x{size}", variable=var).grid(row=row, column=col, sticky="w", padx=10)

# Preview and Convert buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=20)
tk.Button(button_frame, text="Preview Crop", command=preview_cropped_image, 
          bg="lightblue", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Convert to ICO", command=convert_file, 
          bg="lightgreen", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

# Status bar
status_frame = tk.Frame(root, relief=tk.SUNKEN, bd=1)
status_frame.pack(side=tk.BOTTOM, fill=tk.X)
tk.Label(status_frame, textvariable=status_var, anchor=tk.W).pack(fill=tk.X, padx=5, pady=2)

# Instructions
instructions = tk.Text(root, height=8, wrap=tk.WORD)
instructions.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
instructions.insert(tk.END, """Instructions:
1. Select a PNG file with transparency that you want to convert to ICO format
2. Choose where to save the output ICO file (or use the auto-generated name)
3. Select which icon sizes you want to include in the ICO file
4. Click 'Preview Crop' to see how much transparent space will be removed
5. Click 'Convert to ICO' to create your Windows-compatible icon file

Features:
• Automatically crops excess transparent pixels around your image
• Creates multi-size ICO files compatible with Windows
• Maintains transparency and image quality
• Supports common icon sizes from 16x16 to 256x256 pixels""")
instructions.config(state=tk.DISABLED)

if __name__ == "__main__":
    root.mainloop()
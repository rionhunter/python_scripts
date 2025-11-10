#!/usr/bin/env python3
"""
PNG to ICO Converter - Command Line Version
Converts PNG files with transparency to Windows-compatible ICO files.
Automatically crops excess transparent space around the image.
"""

import argparse
import os
import sys
from PIL import Image

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
        print(f"Original image size: {original_img.size}")
        
        # Crop excess transparent space
        cropped_img = crop_transparent_image(original_img)
        print(f"Cropped image size: {cropped_img.size}")
        
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

def main():
    parser = argparse.ArgumentParser(
        description='Convert PNG files to Windows-compatible ICO files with automatic cropping.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.png                           # Creates input.ico with all standard sizes
  %(prog)s input.png -o icon.ico               # Specify output filename
  %(prog)s input.png -s 16 32 48 64            # Only create specific sizes
  %(prog)s input.png -s 16 32 64 -o small.ico # Combine custom sizes with output name
        """
    )
    
    parser.add_argument('input', help='Input PNG file path')
    parser.add_argument('-o', '--output', help='Output ICO file path (default: same as input with .ico extension)')
    parser.add_argument('-s', '--sizes', type=int, nargs='+', 
                       default=[16, 20, 24, 32, 40, 48, 64, 96, 128, 256],
                       help='Icon sizes to include (default: 16 20 24 32 40 48 64 96 128 256)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.", file=sys.stderr)
        return 1
    
    # Check if input is a PNG file
    if not args.input.lower().endswith('.png'):
        print(f"Warning: Input file '{args.input}' does not have .png extension.")
    
    # Generate output filename if not provided
    if args.output is None:
        base_name = os.path.splitext(args.input)[0]
        args.output = base_name + '.ico'
    
    # Validate sizes
    valid_sizes = [size for size in args.sizes if 1 <= size <= 256]
    if not valid_sizes:
        print("Error: No valid icon sizes provided. Sizes must be between 1 and 256.", file=sys.stderr)
        return 1
    
    if len(valid_sizes) != len(args.sizes):
        invalid_sizes = [size for size in args.sizes if size not in valid_sizes]
        print(f"Warning: Ignoring invalid sizes: {invalid_sizes}")
    
    # Sort sizes for consistency
    valid_sizes.sort()
    
    if args.verbose:
        print(f"Input file: {args.input}")
        print(f"Output file: {args.output}")
        print(f"Icon sizes: {valid_sizes}")
        print()
    
    # Perform conversion
    success, message = create_ico_from_png(args.input, args.output, valid_sizes)
    
    if success:
        print(f"✓ {message}")
        if os.path.exists(args.output):
            file_size = os.path.getsize(args.output)
            print(f"✓ ICO file created: {args.output} ({file_size} bytes)")
        return 0
    else:
        print(f"✗ {message}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
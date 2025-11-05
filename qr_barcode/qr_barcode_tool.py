#!/usr/bin/env python3
"""
QR Code and Barcode Generator/Scanner
Generate and read QR codes and barcodes in various formats
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List

# Check for required libraries
QR_AVAILABLE = False
BARCODE_AVAILABLE = False
READER_AVAILABLE = False

try:
    import qrcode
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer
    from qrcode.image.styles.colormasks import SolidFillColorMask
    QR_AVAILABLE = True
except ImportError:
    pass

try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    pass

try:
    from pyzbar import pyzbar
    from PIL import Image
    READER_AVAILABLE = True
except ImportError:
    pass


class QRCodeGenerator:
    """Generate QR codes with customization"""
    
    def __init__(self):
        if not QR_AVAILABLE:
            raise ImportError("QR code generation requires: pip install qrcode[pil]")
    
    def generate(self, data: str, output_path: str, 
                 size: int = 10, border: int = 4,
                 fg_color: str = 'black', bg_color: str = 'white',
                 style: str = 'square') -> None:
        """
        Generate QR code
        
        Args:
            data: Data to encode
            output_path: Output image path
            size: Box size (default: 10)
            border: Border size in boxes (default: 4)
            fg_color: Foreground color (default: black)
            bg_color: Background color (default: white)
            style: Module style ('square', 'rounded', 'circle')
        """
        qr = qrcode.QRCode(
            version=None,  # Auto-determine version
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Apply style
        if style == 'rounded':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=SolidFillColorMask(back_color=bg_color, front_color=fg_color)
            )
        elif style == 'circle':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=CircleModuleDrawer(),
                color_mask=SolidFillColorMask(back_color=bg_color, front_color=fg_color)
            )
        else:  # square
            img = qr.make_image(fill_color=fg_color, back_color=bg_color)
        
        img.save(output_path)
        print(f"QR code saved to: {output_path}")
    
    def generate_batch(self, data_list: List[str], output_dir: str,
                      prefix: str = 'qr', **kwargs) -> None:
        """Generate multiple QR codes"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, data in enumerate(data_list, 1):
            output_path = output_dir / f"{prefix}_{i:04d}.png"
            self.generate(data, str(output_path), **kwargs)


class BarcodeGenerator:
    """Generate barcodes in various formats"""
    
    FORMATS = {
        'ean13': 'ean13',
        'ean8': 'ean8',
        'upc': 'upca',
        'code39': 'code39',
        'code128': 'code128',
        'isbn': 'isbn',
        'isbn13': 'isbn13',
        'isbn10': 'isbn10',
        'issn': 'issn',
        'gs1': 'gs1',
    }
    
    def __init__(self):
        if not BARCODE_AVAILABLE:
            raise ImportError("Barcode generation requires: pip install python-barcode[images]")
    
    def generate(self, data: str, output_path: str, 
                 format: str = 'code128', text: Optional[str] = None) -> None:
        """
        Generate barcode
        
        Args:
            data: Data to encode
            output_path: Output image path (without extension)
            format: Barcode format (default: code128)
            text: Text to display below barcode
        """
        format = self.FORMATS.get(format.lower(), format)
        
        try:
            barcode_class = barcode.get_barcode_class(format)
            barcode_instance = barcode_class(data, writer=ImageWriter())
            
            # Generate and save
            options = {}
            if text:
                options['text'] = text
            
            output_path = Path(output_path)
            # Remove extension if provided (library adds it)
            if output_path.suffix:
                output_path = output_path.with_suffix('')
            
            saved_path = barcode_instance.save(str(output_path), options=options)
            print(f"Barcode saved to: {saved_path}")
        
        except Exception as e:
            print(f"Error generating barcode: {e}")
            raise
    
    def list_formats(self) -> List[str]:
        """List available barcode formats"""
        return list(self.FORMATS.keys())


class CodeReader:
    """Read QR codes and barcodes from images"""
    
    def __init__(self):
        if not READER_AVAILABLE:
            raise ImportError("Code reading requires: pip install pyzbar pillow")
    
    def read(self, image_path: str) -> List[dict]:
        """
        Read QR codes and barcodes from image
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of detected codes with data and type
        """
        try:
            img = Image.open(image_path)
            decoded_objects = pyzbar.decode(img)
            
            results = []
            for obj in decoded_objects:
                results.append({
                    'type': obj.type,
                    'data': obj.data.decode('utf-8'),
                    'quality': obj.quality,
                    'rect': {
                        'left': obj.rect.left,
                        'top': obj.rect.top,
                        'width': obj.rect.width,
                        'height': obj.rect.height
                    }
                })
            
            return results
        
        except Exception as e:
            print(f"Error reading image: {e}")
            return []
    
    def read_batch(self, image_dir: str, pattern: str = '*.png') -> dict:
        """Read codes from multiple images"""
        image_dir = Path(image_dir)
        results = {}
        
        for image_path in image_dir.glob(pattern):
            codes = self.read(str(image_path))
            if codes:
                results[str(image_path)] = codes
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='QR Code and Barcode Generator/Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate QR code
  python qr_barcode_tool.py generate qr "https://example.com" -o qrcode.png
  
  # Generate QR code with style
  python qr_barcode_tool.py generate qr "Hello World" -o qr.png --style rounded --fg-color blue
  
  # Generate barcode
  python qr_barcode_tool.py generate barcode "123456789012" -o barcode --format ean13
  
  # Generate Code128 barcode
  python qr_barcode_tool.py generate barcode "HELLO123" -o code --format code128
  
  # Read QR code/barcode from image
  python qr_barcode_tool.py read qrcode.png
  
  # Batch generate QR codes from file (one per line)
  python qr_barcode_tool.py batch qr urls.txt output_dir
  
  # List barcode formats
  python qr_barcode_tool.py formats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate QR code or barcode')
    gen_parser.add_argument('type', choices=['qr', 'barcode'], help='Code type')
    gen_parser.add_argument('data', help='Data to encode')
    gen_parser.add_argument('-o', '--output', required=True, help='Output file path')
    gen_parser.add_argument('--format', default='code128',
                           help='Barcode format (default: code128)')
    gen_parser.add_argument('--size', type=int, default=10,
                           help='QR code box size (default: 10)')
    gen_parser.add_argument('--border', type=int, default=4,
                           help='QR code border (default: 4)')
    gen_parser.add_argument('--fg-color', default='black',
                           help='QR code foreground color (default: black)')
    gen_parser.add_argument('--bg-color', default='white',
                           help='QR code background color (default: white)')
    gen_parser.add_argument('--style', choices=['square', 'rounded', 'circle'],
                           default='square', help='QR code style (default: square)')
    gen_parser.add_argument('--text', help='Text to display below barcode')
    
    # Read command
    read_parser = subparsers.add_parser('read', help='Read QR code or barcode from image')
    read_parser.add_argument('image', help='Image file path')
    read_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch generate codes')
    batch_parser.add_argument('type', choices=['qr', 'barcode'], help='Code type')
    batch_parser.add_argument('input', help='Input file (one value per line)')
    batch_parser.add_argument('output_dir', help='Output directory')
    batch_parser.add_argument('--format', default='code128',
                             help='Barcode format (default: code128)')
    batch_parser.add_argument('--prefix', default='code', help='Output file prefix')
    
    # Formats command
    subparsers.add_parser('formats', help='List available barcode formats')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Generate
        if args.command == 'generate':
            if args.type == 'qr':
                gen = QRCodeGenerator()
                gen.generate(
                    args.data, args.output,
                    size=args.size, border=args.border,
                    fg_color=args.fg_color, bg_color=args.bg_color,
                    style=args.style
                )
            else:  # barcode
                gen = BarcodeGenerator()
                gen.generate(args.data, args.output, format=args.format, text=args.text)
        
        # Read
        elif args.command == 'read':
            reader = CodeReader()
            results = reader.read(args.image)
            
            if not results:
                print("No codes detected in image")
                return 1
            
            if args.json:
                import json
                print(json.dumps(results, indent=2))
            else:
                for i, code in enumerate(results, 1):
                    print(f"\nCode #{i}:")
                    print(f"  Type: {code['type']}")
                    print(f"  Data: {code['data']}")
                    print(f"  Quality: {code['quality']}")
        
        # Batch
        elif args.command == 'batch':
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Input file not found: {args.input}")
                return 1
            
            # Read data from file
            with open(input_path, 'r', encoding='utf-8') as f:
                data_list = [line.strip() for line in f if line.strip()]
            
            if args.type == 'qr':
                gen = QRCodeGenerator()
                gen.generate_batch(data_list, args.output_dir, prefix=args.prefix)
            else:  # barcode
                gen = BarcodeGenerator()
                output_dir = Path(args.output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                for i, data in enumerate(data_list, 1):
                    output_path = output_dir / f"{args.prefix}_{i:04d}"
                    gen.generate(data, str(output_path), format=args.format)
            
            print(f"Generated {len(data_list)} codes in {args.output_dir}")
        
        # Formats
        elif args.command == 'formats':
            gen = BarcodeGenerator()
            formats = gen.list_formats()
            print("Available barcode formats:")
            for fmt in sorted(formats):
                print(f"  - {fmt}")
        
        return 0
    
    except ImportError as e:
        print(f"Error: {e}")
        print("\nInstall required packages:")
        print("  pip install qrcode[pil] python-barcode[images] pyzbar pillow")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

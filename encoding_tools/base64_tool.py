#!/usr/bin/env python3
"""
Base64 Tools
Encode/decode Base64, view Base64 images, batch processing
"""

import argparse
import sys
import base64
from pathlib import Path
from typing import Optional
import io

# PIL is optional for image viewing
PIL_AVAILABLE = False
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    pass


class Base64Tool:
    """Base64 encoding/decoding utilities"""
    
    @staticmethod
    def encode_string(text: str, encoding: str = 'utf-8') -> str:
        """Encode string to Base64"""
        encoded = base64.b64encode(text.encode(encoding))
        return encoded.decode('ascii')
    
    @staticmethod
    def decode_string(b64_string: str, encoding: str = 'utf-8') -> str:
        """Decode Base64 string"""
        decoded = base64.b64decode(b64_string)
        return decoded.decode(encoding)
    
    @staticmethod
    def encode_file(file_path: str) -> str:
        """Encode file to Base64"""
        with open(file_path, 'rb') as f:
            encoded = base64.b64encode(f.read())
        return encoded.decode('ascii')
    
    @staticmethod
    def decode_file(b64_string: str, output_path: str) -> None:
        """Decode Base64 string to file"""
        decoded = base64.b64decode(b64_string)
        with open(output_path, 'wb') as f:
            f.write(decoded)
    
    @staticmethod
    def encode_image_to_data_uri(image_path: str) -> str:
        """Encode image to data URI (for HTML/CSS)"""
        # Detect MIME type from extension
        ext = Path(image_path).suffix.lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp',
            '.ico': 'image/x-icon'
        }
        mime_type = mime_types.get(ext, 'application/octet-stream')
        
        with open(image_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('ascii')
        
        return f"data:{mime_type};base64,{encoded}"
    
    @staticmethod
    def decode_data_uri(data_uri: str, output_path: Optional[str] = None) -> bytes:
        """Decode data URI"""
        # Parse data URI
        if not data_uri.startswith('data:'):
            raise ValueError("Invalid data URI format")
        
        # Split header and data
        header, data = data_uri.split(',', 1)
        
        # Decode
        decoded = base64.b64decode(data)
        
        # Save if output path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(decoded)
        
        return decoded
    
    @staticmethod
    def view_base64_image(b64_string: str, is_data_uri: bool = False):
        """View Base64 encoded image"""
        if not PIL_AVAILABLE:
            raise ImportError("Image viewing requires: pip install pillow")
        
        try:
            if is_data_uri:
                # Extract base64 from data URI
                if ',' in b64_string:
                    b64_string = b64_string.split(',', 1)[1]
            
            # Decode and open
            img_data = base64.b64decode(b64_string)
            img = Image.open(io.BytesIO(img_data))
            img.show()
            
            print(f"Image displayed: {img.format} {img.size} {img.mode}")
        
        except Exception as e:
            print(f"Error displaying image: {e}")
    
    @staticmethod
    def get_info(b64_string: str, is_data_uri: bool = False) -> dict:
        """Get information about Base64 data"""
        info = {}
        
        if is_data_uri:
            if not b64_string.startswith('data:'):
                raise ValueError("Invalid data URI")
            
            # Parse header
            header, data = b64_string.split(',', 1)
            mime_type = header.split(';')[0].replace('data:', '')
            
            info['type'] = 'data_uri'
            info['mime_type'] = mime_type
            info['base64_length'] = len(data)
            
            # Decode to get actual size
            decoded = base64.b64decode(data)
            info['decoded_size'] = len(decoded)
        else:
            info['type'] = 'base64'
            info['base64_length'] = len(b64_string)
            
            try:
                decoded = base64.b64decode(b64_string)
                info['decoded_size'] = len(decoded)
                info['valid'] = True
            except Exception:
                info['valid'] = False
        
        return info


class Base64BatchProcessor:
    """Batch processing for Base64 operations"""
    
    @staticmethod
    def encode_directory(input_dir: str, output_file: str, 
                        pattern: str = '*', include_subdirs: bool = False):
        """Encode all files in directory to Base64 JSON"""
        import json
        
        input_dir = Path(input_dir)
        encoded_files = {}
        
        # Find files
        if include_subdirs:
            files = input_dir.rglob(pattern)
        else:
            files = input_dir.glob(pattern)
        
        for file_path in files:
            if file_path.is_file():
                relative_path = str(file_path.relative_to(input_dir))
                with open(file_path, 'rb') as f:
                    encoded = base64.b64encode(f.read()).decode('ascii')
                encoded_files[relative_path] = encoded
                print(f"Encoded: {relative_path}")
        
        # Save to JSON
        with open(output_file, 'w') as f:
            json.dump(encoded_files, f, indent=2)
        
        print(f"\nEncoded {len(encoded_files)} files to {output_file}")
    
    @staticmethod
    def decode_directory(input_file: str, output_dir: str):
        """Decode Base64 JSON back to files"""
        import json
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load JSON
        with open(input_file, 'r') as f:
            encoded_files = json.load(f)
        
        # Decode each file
        for relative_path, encoded in encoded_files.items():
            output_path = output_dir / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            decoded = base64.b64decode(encoded)
            with open(output_path, 'wb') as f:
                f.write(decoded)
            
            print(f"Decoded: {relative_path}")
        
        print(f"\nDecoded {len(encoded_files)} files to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Base64 Tools - Encode/decode Base64, view images, batch processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encode string
  python base64_tool.py encode "Hello World"
  
  # Decode string
  python base64_tool.py decode "SGVsbG8gV29ybGQ="
  
  # Encode file
  python base64_tool.py encode-file input.txt -o output.b64
  
  # Decode file
  python base64_tool.py decode-file input.b64 -o output.txt
  
  # Encode image to data URI
  python base64_tool.py image-uri image.png
  
  # View Base64 encoded image
  python base64_tool.py view-image "iVBORw0KGgoAAAANS..."
  
  # Get info about Base64 data
  python base64_tool.py info "SGVsbG8gV29ybGQ="
  
  # Batch encode directory
  python base64_tool.py batch-encode input_dir encoded.json
  
  # Batch decode directory
  python base64_tool.py batch-decode encoded.json output_dir
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Encode string
    enc_parser = subparsers.add_parser('encode', help='Encode string to Base64')
    enc_parser.add_argument('text', help='Text to encode')
    enc_parser.add_argument('--encoding', default='utf-8', help='Text encoding (default: utf-8)')
    
    # Decode string
    dec_parser = subparsers.add_parser('decode', help='Decode Base64 string')
    dec_parser.add_argument('base64', help='Base64 string to decode')
    dec_parser.add_argument('--encoding', default='utf-8', help='Text encoding (default: utf-8)')
    
    # Encode file
    encfile_parser = subparsers.add_parser('encode-file', help='Encode file to Base64')
    encfile_parser.add_argument('input', help='Input file path')
    encfile_parser.add_argument('-o', '--output', help='Output file path')
    
    # Decode file
    decfile_parser = subparsers.add_parser('decode-file', help='Decode Base64 to file')
    decfile_parser.add_argument('input', help='Input Base64 file or string')
    decfile_parser.add_argument('-o', '--output', required=True, help='Output file path')
    decfile_parser.add_argument('--from-file', action='store_true',
                               help='Input is a file containing Base64')
    
    # Image data URI
    imguri_parser = subparsers.add_parser('image-uri', help='Encode image to data URI')
    imguri_parser.add_argument('image', help='Image file path')
    imguri_parser.add_argument('-o', '--output', help='Output file path')
    
    # View image
    view_parser = subparsers.add_parser('view-image', help='View Base64 encoded image')
    view_parser.add_argument('base64', help='Base64 string or data URI')
    view_parser.add_argument('--data-uri', action='store_true', help='Input is data URI')
    
    # Info
    info_parser = subparsers.add_parser('info', help='Get info about Base64 data')
    info_parser.add_argument('base64', help='Base64 string or data URI')
    info_parser.add_argument('--data-uri', action='store_true', help='Input is data URI')
    
    # Batch encode
    batchenc_parser = subparsers.add_parser('batch-encode', help='Batch encode directory')
    batchenc_parser.add_argument('input_dir', help='Input directory')
    batchenc_parser.add_argument('output', help='Output JSON file')
    batchenc_parser.add_argument('--pattern', default='*', help='File pattern (default: *)')
    batchenc_parser.add_argument('-r', '--recursive', action='store_true',
                                help='Include subdirectories')
    
    # Batch decode
    batchdec_parser = subparsers.add_parser('batch-decode', help='Batch decode from JSON')
    batchdec_parser.add_argument('input', help='Input JSON file')
    batchdec_parser.add_argument('output_dir', help='Output directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    tool = Base64Tool()
    
    try:
        # Encode string
        if args.command == 'encode':
            result = tool.encode_string(args.text, encoding=args.encoding)
            print(result)
        
        # Decode string
        elif args.command == 'decode':
            result = tool.decode_string(args.base64, encoding=args.encoding)
            print(result)
        
        # Encode file
        elif args.command == 'encode-file':
            result = tool.encode_file(args.input)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(result)
                print(f"Encoded to: {args.output}")
            else:
                print(result)
        
        # Decode file
        elif args.command == 'decode-file':
            if args.from_file:
                with open(args.input, 'r') as f:
                    b64_data = f.read().strip()
            else:
                b64_data = args.input
            
            tool.decode_file(b64_data, args.output)
            print(f"Decoded to: {args.output}")
        
        # Image data URI
        elif args.command == 'image-uri':
            result = tool.encode_image_to_data_uri(args.image)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(result)
                print(f"Data URI saved to: {args.output}")
            else:
                print(result)
        
        # View image
        elif args.command == 'view-image':
            tool.view_base64_image(args.base64, is_data_uri=args.data_uri)
        
        # Info
        elif args.command == 'info':
            info = tool.get_info(args.base64, is_data_uri=args.data_uri)
            print("Base64 Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        
        # Batch encode
        elif args.command == 'batch-encode':
            processor = Base64BatchProcessor()
            processor.encode_directory(
                args.input_dir, args.output,
                pattern=args.pattern, include_subdirs=args.recursive
            )
        
        # Batch decode
        elif args.command == 'batch-decode':
            processor = Base64BatchProcessor()
            processor.decode_directory(args.input, args.output_dir)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

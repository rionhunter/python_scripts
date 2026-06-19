"""File processing utilities for the text file compiler."""

import os
import re
try:
    import chardet
except Exception:
    chardet = None
from typing import List, Optional, Tuple
from pathlib import Path


class FileProcessor:
    """Utility class for file processing operations."""

    @staticmethod
    def remove_trailing_whitespace(content: str) -> str:
        """Strip trailing spaces and tabs from each line while preserving line endings."""
        normalized_lines = []
        for line in content.splitlines(keepends=True):
            line_body = line.rstrip('\r\n').rstrip(' \t')
            line_ending = line[len(line.rstrip('\r\n')):]
            normalized_lines.append(f"{line_body}{line_ending}")

        if not normalized_lines:
            return content.rstrip(' \t')

        return ''.join(normalized_lines)

    @staticmethod
    def natural_sort_key(value: str) -> tuple:
        """Create a case-insensitive natural sort key for names with numbers."""
        parts = re.split(r'(\d+)', value.lower())
        return tuple(int(part) if part.isdigit() else part for part in parts)
    
    @staticmethod
    def read_file_with_encoding(file_path: str) -> Tuple[str, str]:
        """
        Read a file and detect its encoding.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (file_content, encoding)
            
        Raises:
            IOError: If file cannot be read
        """
        try:
            # First try to detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                
            if not raw_data:
                return "", "utf-8"
                
            # Detect encoding (use chardet if available)
            if chardet:
                detected = chardet.detect(raw_data)
                encoding = detected.get('encoding', 'utf-8')
            else:
                encoding = 'utf-8'
            
            # Fallback encodings to try
            encodings_to_try = [encoding, 'utf-8', 'latin-1', 'cp1252']
            
            for enc in encodings_to_try:
                if enc:
                    try:
                        content = raw_data.decode(enc)
                        return content, enc
                    except (UnicodeDecodeError, LookupError):
                        continue
            
            # If all fail, use utf-8 with error handling
            content = raw_data.decode('utf-8', errors='replace')
            return content, 'utf-8'
            
        except IOError as e:
            raise IOError(f"Failed to read file {file_path}: {e}")
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'is_text': FileProcessor.is_text_file(file_path),
                'extension': Path(file_path).suffix.lower()
            }
        except OSError:
            return {
                'size': 0,
                'modified': 0,
                'is_text': False,
                'extension': ''
            }
    
    @staticmethod
    def is_text_file(file_path: str) -> bool:
        """
        Check if a file is likely a text file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is likely text
        """
        # Check extension first
        text_extensions = {
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml',
            '.yml', '.yaml', '.ini', '.cfg', '.conf', '.log', '.csv',
            '.rst', '.tex', '.sh', '.bat', '.ps1', '.php', '.rb', '.go',
            '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.vb', '.sql'
        }
        
        ext = Path(file_path).suffix.lower()
        if ext in text_extensions:
            return True
        
        # Check content for small files
        try:
            if os.path.getsize(file_path) > 1024 * 1024:  # Skip files larger than 1MB
                return False
                
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                
            if not chunk:
                return True  # Empty file is considered text
                
            # Check for null bytes (binary indicator)
            if b'\x00' in chunk:
                return False
                
            # Try to decode as text
            try:
                chunk.decode('utf-8')
                return True
            except UnicodeDecodeError:
                try:
                    chunk.decode('latin-1')
                    return True
                except UnicodeDecodeError:
                    return False
                    
        except (OSError, IOError):
            return False
    
    @staticmethod
    def scan_directory(directory: str, include_hidden: bool = False) -> List[dict]:
        """
        Scan a directory for files and subdirectories.
        
        Args:
            directory: Directory to scan
            include_hidden: Whether to include hidden files/directories
            
        Returns:
            List of file/directory information dictionaries
        """
        items = []
        
        try:
            for item in os.listdir(directory):
                if not include_hidden and item.startswith('.'):
                    continue
                    
                item_path = os.path.join(directory, item)
                
                try:
                    is_dir = os.path.isdir(item_path)
                    stat_info = os.stat(item_path)
                    
                    item_info = {
                        'name': item,
                        'path': item_path,
                        'is_directory': is_dir,
                        'size': stat_info.st_size if not is_dir else 0,
                        'modified': stat_info.st_mtime,
                        'is_text': False if is_dir else FileProcessor.is_text_file(item_path)
                    }
                    
                    items.append(item_info)
                    
                except (OSError, IOError):
                    # Skip items we can't access
                    continue
                    
        except (OSError, IOError):
            # Return empty list if directory can't be read
            pass
            
        # Sort: directories first, then files, using natural ordering.
        items.sort(key=lambda x: (not x['is_directory'], FileProcessor.natural_sort_key(x['name'])))
        return items

    @staticmethod
    def collect_text_files(directory: str, recursive: bool = True, include_hidden: bool = False) -> List[str]:
        """Collect text files from a directory in stable logical order."""
        collected: List[str] = []

        if not os.path.isdir(directory):
            return collected

        if recursive:
            for root, dirs, files in os.walk(directory):
                if not include_hidden:
                    dirs[:] = [name for name in dirs if not name.startswith('.')]
                    files = [name for name in files if not name.startswith('.')]

                dirs.sort(key=FileProcessor.natural_sort_key)
                for file_name in sorted(files, key=FileProcessor.natural_sort_key):
                    file_path = os.path.join(root, file_name)
                    if os.path.isfile(file_path) and FileProcessor.is_text_file(file_path):
                        collected.append(file_path)
            return collected

        for item in FileProcessor.scan_directory(directory, include_hidden=include_hidden):
            if item['is_directory']:
                continue
            if item['is_text'] and os.path.isfile(item['path']):
                collected.append(item['path'])

        return collected
    
    @staticmethod
    def create_file_tree(directory: str, max_depth: int = 3, current_depth: int = 0) -> str:
        """
        Create a text representation of a directory tree.
        
        Args:
            directory: Root directory
            max_depth: Maximum depth to scan
            current_depth: Current depth (for recursion)
            
        Returns:
            String representation of the tree
        """
        if current_depth >= max_depth:
            return ""
            
        tree = ""
        try:
            items = FileProcessor.scan_directory(directory, include_hidden=False)
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                prefix = "└── " if is_last else "├── "
                tree += "    " * current_depth + prefix + item['name']
                
                if item['is_directory']:
                    tree += "/\n"
                    if current_depth < max_depth - 1:
                        subtree = FileProcessor.create_file_tree(
                            item['path'], max_depth, current_depth + 1
                        )
                        if subtree:
                            tree += subtree
                else:
                    tree += "\n"
                    
        except (OSError, IOError):
            pass
            
        return tree
    
    @staticmethod
    def get_relative_path(file_path: str, base_path: str) -> str:
        """
        Get relative path from base path.
        
        Args:
            file_path: Full file path
            base_path: Base directory path
            
        Returns:
            Relative path
        """
        try:
            return os.path.relpath(file_path, base_path)
        except ValueError:
            # Paths are on different drives (Windows)
            return file_path
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
            
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"
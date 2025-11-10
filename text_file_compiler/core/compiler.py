"""Core compilation logic for the text file compiler."""

import os
from datetime import datetime
from typing import List, Dict, Any
from .file_processor import FileProcessor


class Compiler:
    """Main compiler class for combining text/markdown files."""
    
    def __init__(self):
        self.file_processor = FileProcessor()
    
    def compile_files(self, files: List[str], project_config: Dict[str, Any]) -> str:
        """
        Compile multiple files into a single text output.
        
        Args:
            files: List of file paths to compile
            project_config: Project configuration dictionary
            
        Returns:
            Compiled text content
        """
        output_parts = []
        
        # Add project header
        output_parts.append(self._create_header(project_config))
        
        # Add file tree if enabled
        if project_config.get('output_settings', {}).get('include_file_tree', True):
            file_tree = self._create_file_tree_for_files(files)
            if file_tree:
                output_parts.append(f"## File Structure\n\n```\n{file_tree}```\n")
        
        # Process each file
        for file_path in files:
            try:
                file_content = self._process_file(file_path, project_config)
                if file_content:
                    output_parts.append(file_content)
            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                output_parts.append(f"```\n{error_msg}\n```\n")
        
        # Add footer
        output_parts.append(self._create_footer(files))
        
        return "\n".join(output_parts)
    
    def _create_header(self, project_config: Dict[str, Any]) -> str:
        """Create the header section of the compiled output."""
        project_name = project_config.get('name', 'Untitled Project')
        project_description = project_config.get('description', '')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        header = f"# {project_name}\n\n"
        
        if project_description:
            header += f"**Description:** {project_description}\n\n"
        
        header += f"**Compiled:** {timestamp}\n\n"
        header += "---\n\n"
        
        return header
    
    def _create_footer(self, files: List[str]) -> str:
        """Create the footer section of the compiled output."""
        file_count = len(files)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        footer = "\n---\n\n"
        footer += f"**Compilation Summary**\n\n"
        footer += f"- Files processed: {file_count}\n"
        footer += f"- Generated: {timestamp}\n"
        
        return footer
    
    def _process_file(self, file_path: str, project_config: Dict[str, Any]) -> str:
        """Process a single file and return its formatted content."""
        if not os.path.exists(file_path):
            return f"```\nFile not found: {file_path}\n```\n"
        
        # Check if file is text
        if not self.file_processor.is_text_file(file_path):
            file_info = self.file_processor.get_file_info(file_path)
            size_str = self.file_processor.format_file_size(file_info['size'])
            return f"```\nBinary file: {file_path} ({size_str})\n```\n"
        
        try:
            content, encoding = self.file_processor.read_file_with_encoding(file_path)
            
            output_parts = []
            
            # Add file header if enabled
            if project_config.get('output_settings', {}).get('include_file_names', True):
                file_name = os.path.basename(file_path)
                rel_path = self._get_display_path(file_path)
                
                output_parts.append(f"## {file_name}")
                output_parts.append(f"**Path:** `{rel_path}`")
                
                # Add file info
                file_info = self.file_processor.get_file_info(file_path)
                size_str = self.file_processor.format_file_size(file_info['size'])
                output_parts.append(f"**Size:** {size_str}")
                output_parts.append(f"**Encoding:** {encoding}")
                output_parts.append("")
            
            # Add file content
            if content.strip():
                # Detect file type for syntax highlighting
                file_ext = os.path.splitext(file_path)[1].lower()
                language = self._get_language_from_extension(file_ext)
                
                if language:
                    output_parts.append(f"```{language}")
                    output_parts.append(content)
                    output_parts.append("```")
                else:
                    output_parts.append("```")
                    output_parts.append(content)
                    output_parts.append("```")
            else:
                output_parts.append("```\n(Empty file)\n```")
            
            output_parts.append("")  # Add spacing
            
            return "\n".join(output_parts)
            
        except Exception as e:
            return f"```\nError reading {file_path}: {str(e)}\n```\n"
    
    def _get_display_path(self, file_path: str) -> str:
        """Get a display-friendly file path."""
        # Try to make path relative to user home directory
        try:
            home = os.path.expanduser("~")
            if file_path.startswith(home):
                return "~" + file_path[len(home):]
        except:
            pass
        
        return file_path
    
    def _get_language_from_extension(self, extension: str) -> str:
        """Get syntax highlighting language from file extension."""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'zsh',
            '.ps1': 'powershell',
            '.bat': 'batch',
            '.cmd': 'batch',
            '.html': 'html',
            '.htm': 'html',
            '.xml': 'xml',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'ini',
            '.conf': 'conf',
            '.sql': 'sql',
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.rst': 'rst',
            '.tex': 'latex',
            '.r': 'r',
            '.R': 'r',
            '.m': 'matlab',
            '.pl': 'perl',
            '.lua': 'lua',
            '.vim': 'vim',
            '.dockerfile': 'dockerfile',
            '.gitignore': 'gitignore',
            '.gitattributes': 'gitattributes'
        }
        
        return language_map.get(extension, '')
    
    def _create_file_tree_for_files(self, files: List[str]) -> str:
        """Create a file tree representation for the selected files."""
        if not files:
            return ""
        
        # Group files by directory
        dirs = {}
        for file_path in files:
            dir_path = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            
            if dir_path not in dirs:
                dirs[dir_path] = []
            dirs[dir_path].append(file_name)
        
        # Build tree representation
        tree_lines = []
        
        # Find common root
        if len(dirs) > 1:
            common_path = os.path.commonpath(list(dirs.keys()))
            if common_path:
                tree_lines.append(f"{os.path.basename(common_path) or 'Root'}/")
        
        sorted_dirs = sorted(dirs.keys())
        for i, dir_path in enumerate(sorted_dirs):
            is_last_dir = i == len(sorted_dirs) - 1
            
            # Add directory name
            dir_name = os.path.basename(dir_path) or dir_path
            if len(sorted_dirs) > 1:
                dir_prefix = "└── " if is_last_dir else "├── "
                tree_lines.append(f"{dir_prefix}{dir_name}/")
                file_prefix = "    " if is_last_dir else "│   "
            else:
                tree_lines.append(f"{dir_name}/")
                file_prefix = ""
            
            # Add files in directory
            files_in_dir = sorted(dirs[dir_path])
            for j, file_name in enumerate(files_in_dir):
                is_last_file = j == len(files_in_dir) - 1
                file_symbol = "└── " if is_last_file else "├── "
                tree_lines.append(f"{file_prefix}{file_symbol}{file_name}")
        
        return "\n".join(tree_lines)
    
    def get_compilation_stats(self, files: List[str]) -> Dict[str, Any]:
        """Get statistics about the files to be compiled."""
        stats = {
            'total_files': len(files),
            'text_files': 0,
            'binary_files': 0,
            'total_size': 0,
            'extensions': {},
            'missing_files': 0
        }
        
        for file_path in files:
            if not os.path.exists(file_path):
                stats['missing_files'] += 1
                continue
            
            file_info = self.file_processor.get_file_info(file_path)
            stats['total_size'] += file_info['size']
            
            if file_info['is_text']:
                stats['text_files'] += 1
            else:
                stats['binary_files'] += 1
            
            ext = file_info['extension'] or '(no extension)'
            stats['extensions'][ext] = stats['extensions'].get(ext, 0) + 1
        
        return stats
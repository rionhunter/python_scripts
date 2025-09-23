#!/usr/bin/env python3
"""Test script for the text file compiler core functionality."""

import os
import sys
import tempfile
import json

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.compiler import Compiler
from core.file_processor import FileProcessor
from settings.config import ProjectConfig


def test_file_processor():
    """Test the FileProcessor functionality."""
    print("Testing FileProcessor...")
    
    processor = FileProcessor()
    
    # Test file size formatting
    assert processor.format_file_size(0) == "0 B"
    assert processor.format_file_size(1024) == "1.0 KB"
    assert processor.format_file_size(1048576) == "1.0 MB"
    print("✓ File size formatting works")
    
    # Test text file detection
    assert processor.is_text_file("test.py")
    assert processor.is_text_file("README.md")
    assert not processor.is_text_file("image.jpg")
    print("✓ Text file detection works")
    
    # Test directory scanning (use current directory)
    items = processor.scan_directory(".")
    assert isinstance(items, list)
    print(f"✓ Directory scanning works (found {len(items)} items)")
    
    print("FileProcessor tests passed!\n")


def test_compiler():
    """Test the Compiler functionality."""
    print("Testing Compiler...")
    
    compiler = Compiler()
    
    # Create temporary test files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_file1 = os.path.join(temp_dir, "test1.py")
        test_file2 = os.path.join(temp_dir, "test2.md")
        
        with open(test_file1, 'w') as f:
            f.write('print("Hello from test1.py")')
        
        with open(test_file2, 'w') as f:
            f.write('# Test Markdown\n\nThis is a test markdown file.')
        
        # Test compilation
        project_config = {
            'name': 'Test Project',
            'description': 'A test project for validation',
            'output_settings': {
                'include_file_names': True,
                'include_file_tree': True
            }
        }
        
        files = [test_file1, test_file2]
        result = compiler.compile_files(files, project_config)
        
        # Verify output contains expected elements
        assert "Test Project" in result
        assert "test1.py" in result
        assert "test2.md" in result
        assert 'print("Hello from test1.py")' in result
        assert "This is a test markdown file." in result
        
        print("✓ File compilation works")
        
        # Test compilation stats
        stats = compiler.get_compilation_stats(files)
        assert stats['total_files'] == 2
        assert stats['text_files'] == 2
        assert stats['binary_files'] == 0
        
        print("✓ Compilation statistics work")
    
    print("Compiler tests passed!\n")


def test_project_config():
    """Test the ProjectConfig functionality."""
    print("Testing ProjectConfig...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_file = os.path.join(temp_dir, "test_project.json")
        
        # Create new project config
        config = ProjectConfig(project_file)
        
        # Test setting values
        config.set_name("Test Project")
        config.set_description("A test project")
        config.add_file("test1.py")
        config.add_file("test2.md")
        config.set_browser_location("/tmp")
        
        # Save project
        config.save_project()
        
        # Verify file was created
        assert os.path.exists(project_file)
        print("✓ Project file creation works")
        
        # Load project and verify data
        config2 = ProjectConfig(project_file)
        assert config2.get_name() == "Test Project"
        assert config2.get_description() == "A test project"
        assert "test1.py" in config2.get_files()
        assert "test2.md" in config2.get_files()
        assert config2.get_browser_location() == "/tmp"
        
        print("✓ Project file loading works")
    
    print("ProjectConfig tests passed!\n")


def test_integration():
    """Test integration between components."""
    print("Testing integration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a sample project
        project_file = os.path.join(temp_dir, "integration_test.json")
        config = ProjectConfig(project_file)
        
        # Create test files
        test_files = []
        for i in range(3):
            test_file = os.path.join(temp_dir, f"test{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"This is test file {i}\nLine 2 of test file {i}")
            test_files.append(test_file)
            config.add_file(test_file)
        
        config.set_name("Integration Test Project")
        config.set_description("Testing integration between components")
        config.save_project()
        
        # Compile the project
        compiler = Compiler()
        result = compiler.compile_files(
            config.get_files(), 
            {
                'name': config.get_name(),
                'description': config.get_description(),
                'output_settings': config.get_output_settings()
            }
        )
        
        # Verify the output
        assert "Integration Test Project" in result
        assert "Testing integration between components" in result
        for i in range(3):
            assert f"test{i}.txt" in result
            assert f"This is test file {i}" in result
        
        print("✓ End-to-end integration works")
    
    print("Integration tests passed!\n")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Text File Compiler - Core Functionality Tests")
    print("=" * 50)
    print()
    
    try:
        test_file_processor()
        test_compiler()
        test_project_config()
        test_integration()
        
        print("=" * 50)
        print("🎉 All tests passed! Core functionality is working correctly.")
        print("=" * 50)
        
        # Display some example usage
        print("\nExample usage:")
        print("1. Create test files in a directory")
        print("2. Run: python main.py")
        print("3. Create a new project")
        print("4. Add files using the file browser")
        print("5. Compile and view the output")
        print("\nNote: GUI requires PyQt6 to be installed: pip install PyQt6>=6.4.0")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
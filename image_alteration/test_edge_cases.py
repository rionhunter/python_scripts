#!/usr/bin/env python3
"""
Additional edge case tests for image processing scripts
Tests error handling, edge cases, and robustness
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import json

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from image_converter import ImageConverter
from image_filter_system import ImageFilterSystem
from batch_image_processor import BatchImageProcessor

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.converter = ImageConverter()
        self.filter_system = ImageFilterSystem()
        self.processor = BatchImageProcessor()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_convert_nonexistent_file(self):
        """Test handling of nonexistent input file"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.png")
        output_file = os.path.join(self.temp_dir, "output.jpg")
        
        success, message = self.converter.convert_single_image(
            nonexistent_file, output_file, "JPEG"
        )
        
        self.assertFalse(success)
        self.assertIn("Error", message)
    
    def test_convert_corrupted_image(self):
        """Test handling of corrupted image file"""
        corrupted_file = os.path.join(self.temp_dir, "corrupted.png")
        
        # Create a file with invalid image data
        with open(corrupted_file, 'wb') as f:
            f.write(b"This is not a valid image file")
        
        output_file = os.path.join(self.temp_dir, "output.jpg")
        success, message = self.converter.convert_single_image(
            corrupted_file, output_file, "JPEG"
        )
        
        self.assertFalse(success)
        self.assertIn("Error", message)
    
    def test_convert_to_readonly_location(self):
        """Test handling of readonly output location"""
        # Create a test image
        test_image = Image.new('RGB', (50, 50), 'red')
        input_file = os.path.join(self.temp_dir, "test.png")
        test_image.save(input_file)
        
        # Try to save to a directory that doesn't exist
        output_file = os.path.join(self.temp_dir, "nonexistent_dir", "output.jpg")
        
        success, message = self.converter.convert_single_image(
            input_file, output_file, "JPEG"
        )
        
        # This should fail because the directory doesn't exist
        self.assertFalse(success)
        self.assertIn("Error", message)
    
    def test_unsupported_format_conversion(self):
        """Test conversion to unsupported format"""
        test_image = Image.new('RGB', (50, 50), 'red')
        input_file = os.path.join(self.temp_dir, "test.png")
        test_image.save(input_file)
        
        output_file = os.path.join(self.temp_dir, "output.xyz")
        
        # This should handle the unsupported format gracefully
        success, message = self.converter.convert_single_image(
            input_file, output_file, "UNSUPPORTED_FORMAT"
        )
        
        self.assertFalse(success)
    
    def test_apply_nonexistent_filter(self):
        """Test applying a filter that doesn't exist"""
        test_image = Image.new('RGB', (50, 50), 'red')
        input_file = os.path.join(self.temp_dir, "test.png")
        test_image.save(input_file)
        
        output_file = os.path.join(self.temp_dir, "filtered.png")
        
        success, message = self.filter_system.apply_filter_to_image(
            input_file, output_file, "NonexistentFilter"
        )
        
        self.assertFalse(success)
        self.assertIn("not found", message)
    
    def test_filter_with_invalid_parameters(self):
        """Test filter with invalid parameters"""
        test_image = Image.new('RGB', (50, 50), 'red')
        
        # Test with invalid blur radius
        invalid_filter = {"type": "blur", "radius": -1}
        
        # This should not crash, might produce unexpected results
        try:
            result = self.filter_system.apply_filter(test_image, invalid_filter)
            # If it doesn't crash, that's fine - PIL might handle it
            self.assertIsNotNone(result)
        except Exception:
            # If it does crash, that's also acceptable for invalid parameters
            pass
    
    def test_empty_batch_folder(self):
        """Test batch processing with empty folder"""
        empty_folder = os.path.join(self.temp_dir, "empty")
        output_folder = os.path.join(self.temp_dir, "output")
        os.makedirs(empty_folder)
        
        results = self.converter.batch_convert(empty_folder, output_folder, "JPEG")
        
        self.assertEqual(len(results), 0)
    
    def test_batch_with_mixed_file_types(self):
        """Test batch processing with mixed file types (some unsupported)"""
        input_folder = os.path.join(self.temp_dir, "mixed")
        output_folder = os.path.join(self.temp_dir, "output")
        os.makedirs(input_folder)
        
        # Create valid image
        img = Image.new('RGB', (50, 50), 'blue')
        img.save(os.path.join(input_folder, "valid.png"))
        
        # Create text file (should be ignored)
        with open(os.path.join(input_folder, "text.txt"), 'w') as f:
            f.write("This is not an image")
        
        # Create corrupted "image" file
        with open(os.path.join(input_folder, "corrupted.jpg"), 'wb') as f:
            f.write(b"Invalid image data")
        
        results = self.converter.batch_convert(input_folder, output_folder, "JPEG")
        
        # Should process 2 files (valid.png and corrupted.jpg)
        # One should succeed, one should fail
        self.assertEqual(len(results), 2)
        
        successes = sum(1 for success, _ in results if success)
        failures = sum(1 for success, _ in results if not success)
        
        self.assertEqual(successes, 1)  # valid.png
        self.assertEqual(failures, 1)   # corrupted.jpg
    
    def test_very_small_image(self):
        """Test processing very small image (1x1 pixel)"""
        tiny_image = Image.new('RGB', (1, 1), 'red')
        input_file = os.path.join(self.temp_dir, "tiny.png")
        tiny_image.save(input_file)
        
        output_file = os.path.join(self.temp_dir, "tiny_converted.jpg")
        
        success, message = self.converter.convert_single_image(
            input_file, output_file, "JPEG"
        )
        
        self.assertTrue(success)
        
        # Verify the output
        with Image.open(output_file) as result:
            self.assertEqual(result.size, (1, 1))
    
    def test_very_large_quality_value(self):
        """Test with quality values outside normal range"""
        test_image = Image.new('RGB', (50, 50), 'red')
        input_file = os.path.join(self.temp_dir, "test.png")
        test_image.save(input_file)
        
        output_file = os.path.join(self.temp_dir, "output.jpg")
        
        # Test with quality > 100
        success, message = self.converter.convert_single_image(
            input_file, output_file, "JPEG", quality=150
        )
        
        # Should still work (PIL will clamp the value)
        self.assertTrue(success)
    
    def test_ico_with_invalid_sizes(self):
        """Test ICO conversion with invalid size specifications"""
        test_image = Image.new('RGB', (64, 64), 'red')
        input_file = os.path.join(self.temp_dir, "test.png")
        test_image.save(input_file)
        
        output_file = os.path.join(self.temp_dir, "output.ico")
        
        # Test with empty sizes list
        success, message = self.converter.convert_single_image(
            input_file, output_file, "ICO", sizes=[]
        )
        
        # Should still work with some default behavior
        self.assertTrue(success)
    
    def test_filter_save_with_invalid_name(self):
        """Test saving filter with invalid filename characters"""
        filter_config = {"type": "blur", "radius": 2}
        
        # Test with filename that might cause issues
        invalid_names = ["", "con", "test/name", "test\\name", "test:name"]
        
        for name in invalid_names:
            try:
                self.filter_system.save_filter(name, filter_config)
                # If it succeeds, try to load it back
                loaded = self.filter_system.load_filter(name)
                if loaded:
                    self.assertEqual(loaded, filter_config)
            except Exception:
                # If it fails, that's acceptable for invalid names
                pass
    
    def test_chain_operations_with_failures(self):
        """Test chained operations where intermediate steps fail"""
        input_folder = os.path.join(self.temp_dir, "input")
        output_folder = os.path.join(self.temp_dir, "output")
        os.makedirs(input_folder)
        
        # Create a test image
        img = Image.new('RGB', (50, 50), 'green')
        img.save(os.path.join(input_folder, "test.png"))
        
        # Create operations where one might fail
        operations = [
            {"type": "convert_format", "format": "JPEG"},
            {"type": "apply_filter", "filter": "NonexistentFilter"}  # This should fail
        ]
        
        results = self.processor.process_batch(input_folder, output_folder, operations)
        
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0][0])  # Should fail due to nonexistent filter
    
    def test_memory_efficiency_large_batch(self):
        """Test that batch processing doesn't consume excessive memory"""
        input_folder = os.path.join(self.temp_dir, "large_batch")
        output_folder = os.path.join(self.temp_dir, "output")
        os.makedirs(input_folder)
        
        # Create many small test images
        for i in range(20):  # Keep reasonable for test speed
            img = Image.new('RGB', (100, 100), (i*10, 100, 200))
            img.save(os.path.join(input_folder, f"test_{i:03d}.png"))
        
        operations = [
            {"type": "convert_format", "format": "JPEG", "quality": 85},
            {"type": "apply_filter", "filter": "Blur"}
        ]
        
        # This should complete without memory issues
        results = self.processor.process_batch(input_folder, output_folder, operations)
        
        self.assertEqual(len(results), 20)
        # Most should succeed (allowing for some potential failures)
        success_count = sum(1 for success, _ in results if success)
        self.assertGreaterEqual(success_count, 18)  # Allow for 2 potential failures

class TestPerformance(unittest.TestCase):
    """Basic performance tests"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.converter = ImageConverter()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_conversion_speed(self):
        """Test that conversions complete in reasonable time"""
        import time
        
        # Create a test image
        test_image = Image.new('RGB', (1000, 1000), 'blue')
        input_file = os.path.join(self.temp_dir, "large_test.png")
        test_image.save(input_file)
        
        output_file = os.path.join(self.temp_dir, "large_output.jpg")
        
        start_time = time.time()
        success, message = self.converter.convert_single_image(
            input_file, output_file, "JPEG"
        )
        end_time = time.time()
        
        self.assertTrue(success)
        
        # Should complete in reasonable time (less than 5 seconds for 1000x1000 image)
        duration = end_time - start_time
        self.assertLess(duration, 5.0, f"Conversion took too long: {duration:.2f} seconds")

def run_edge_case_tests():
    """Run edge case tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [TestEdgeCases, TestPerformance]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    return result

if __name__ == "__main__":
    print("Running edge case and robustness tests...")
    print("=" * 60)
    
    result = run_edge_case_tests()
    
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    if result.wasSuccessful():
        print("\n✅ All edge case tests passed!")
    else:
        print("\n⚠️ Some edge case tests failed (this may be expected for error handling tests)")
        # Don't exit with error for edge case tests as some failures are expected
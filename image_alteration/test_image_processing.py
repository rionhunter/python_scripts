#!/usr/bin/env python3
"""
Comprehensive test suite for image processing scripts
Tests functionality of all image processing modules
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

# Import our modules to test
try:
    from image_converter import ImageConverter
    from image_filter_system import ImageFilterSystem
    from batch_image_processor import BatchImageProcessor
    # Note: raw_converter requires rawpy which might not be installed yet
    try:
        from raw_converter import RawConverter
        RAW_CONVERTER_AVAILABLE = True
    except ImportError:
        RAW_CONVERTER_AVAILABLE = False
        print("Warning: RawConverter not available (rawpy not installed)")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class TestImageConverter(unittest.TestCase):
    """Test the ImageConverter class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.converter = ImageConverter()
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test.png")
        
        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='red')
        test_image.save(self.test_image_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_is_supported_format(self):
        """Test format detection"""
        self.assertTrue(self.converter.is_supported_format("test.jpg"))
        self.assertTrue(self.converter.is_supported_format("test.png"))
        self.assertTrue(self.converter.is_supported_format("test.webp"))
        self.assertFalse(self.converter.is_supported_format("test.txt"))
        self.assertFalse(self.converter.is_supported_format("test.exe"))
    
    def test_convert_single_image_png_to_jpeg(self):
        """Test PNG to JPEG conversion"""
        output_path = os.path.join(self.temp_dir, "output.jpg")
        
        success, message = self.converter.convert_single_image(
            self.test_image_path, output_path, "JPEG", quality=90
        )
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        self.assertIn("Converted", message)
        
        # Verify the output image
        with Image.open(output_path) as img:
            self.assertEqual(img.format, 'JPEG')
            self.assertEqual(img.size, (100, 100))
    
    def test_convert_single_image_png_to_webp(self):
        """Test PNG to WEBP conversion"""
        output_path = os.path.join(self.temp_dir, "output.webp")
        
        success, message = self.converter.convert_single_image(
            self.test_image_path, output_path, "WEBP", quality=85
        )
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify the output image
        with Image.open(output_path) as img:
            self.assertEqual(img.format, 'WEBP')
    
    def test_convert_with_transparency(self):
        """Test conversion handling transparency"""
        # Create PNG with transparency
        rgba_image = Image.new('RGBA', (50, 50), (255, 0, 0, 128))
        rgba_path = os.path.join(self.temp_dir, "transparent.png")
        rgba_image.save(rgba_path)
        
        # Convert to JPEG (should handle transparency)
        jpeg_path = os.path.join(self.temp_dir, "from_transparent.jpg")
        success, message = self.converter.convert_single_image(
            rgba_path, jpeg_path, "JPEG"
        )
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(jpeg_path))
        
        # Verify no transparency in JPEG
        with Image.open(jpeg_path) as img:
            self.assertEqual(img.mode, 'RGB')
    
    def test_batch_convert(self):
        """Test batch conversion"""
        # Create multiple test images
        batch_input = os.path.join(self.temp_dir, "input")
        batch_output = os.path.join(self.temp_dir, "output")
        os.makedirs(batch_input)
        
        # Create test images
        for i in range(3):
            img = Image.new('RGB', (50, 50), (i*80, 100, 200))
            img.save(os.path.join(batch_input, f"test_{i}.png"))
        
        # Run batch conversion
        results = self.converter.batch_convert(batch_input, batch_output, "JPEG")
        
        # Verify results
        self.assertEqual(len(results), 3)
        self.assertTrue(all(success for success, _ in results))
        self.assertTrue(os.path.exists(batch_output))
        
        # Check output files
        output_files = os.listdir(batch_output)
        self.assertEqual(len(output_files), 3)
        self.assertTrue(all(f.endswith('.jpg') for f in output_files))

class TestImageFilterSystem(unittest.TestCase):
    """Test the ImageFilterSystem class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.filter_system = ImageFilterSystem()
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test.png")
        
        # Create a colorful test image
        test_image = Image.new('RGB', (100, 100))
        pixels = []
        for y in range(100):
            for x in range(100):
                pixels.append((x*2, y*2, (x+y) % 255))
        test_image.putdata(pixels)
        test_image.save(self.test_image_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_builtin_filters_exist(self):
        """Test that built-in filters are available"""
        builtin_filters = self.filter_system.builtin_filters
        
        self.assertIn("Blur", builtin_filters)
        self.assertIn("Sharpen", builtin_filters)
        self.assertIn("Grayscale", builtin_filters)
        self.assertIn("Sepia", builtin_filters)
        self.assertIn("Vintage", builtin_filters)
    
    def test_apply_grayscale_filter(self):
        """Test grayscale filter application"""
        with Image.open(self.test_image_path) as img:
            filtered = self.filter_system.apply_filter(img, {"type": "grayscale"})
            
            # Check that image is grayscale (all RGB channels should be equal)
            pixels = list(filtered.getdata())
            sample_pixel = pixels[0]
            # For grayscale images converted back to RGB, R=G=B
            self.assertEqual(sample_pixel[0], sample_pixel[1])
            self.assertEqual(sample_pixel[1], sample_pixel[2])
    
    def test_apply_blur_filter(self):
        """Test blur filter application"""
        with Image.open(self.test_image_path) as img:
            filtered = self.filter_system.apply_filter(img, {"type": "blur", "radius": 2})
            
            # Blurred image should have same size but different content
            self.assertEqual(filtered.size, img.size)
            self.assertNotEqual(list(filtered.getdata()), list(img.getdata()))
    
    def test_apply_enhance_filter(self):
        """Test enhancement filter"""
        with Image.open(self.test_image_path) as img:
            filter_config = {
                "type": "enhance",
                "brightness": 1.2,
                "contrast": 1.1,
                "color": 0.9,
                "sharpness": 1.3
            }
            filtered = self.filter_system.apply_filter(img, filter_config)
            
            self.assertEqual(filtered.size, img.size)
            self.assertEqual(filtered.mode, img.mode)
    
    def test_apply_color_balance_filter(self):
        """Test color balance filter"""
        with Image.open(self.test_image_path) as img:
            filter_config = {
                "type": "color_balance",
                "red": 1.2,
                "green": 0.8,
                "blue": 1.1
            }
            filtered = self.filter_system.apply_filter(img, filter_config)
            
            self.assertEqual(filtered.size, img.size)
            self.assertEqual(filtered.mode, img.mode)
    
    def test_apply_composite_filter(self):
        """Test composite filter (multiple filters)"""
        with Image.open(self.test_image_path) as img:
            filter_config = {
                "type": "composite",
                "filters": [
                    {"type": "enhance", "brightness": 1.1},
                    {"type": "blur", "radius": 1}
                ]
            }
            filtered = self.filter_system.apply_filter(img, filter_config)
            
            self.assertEqual(filtered.size, img.size)
    
    def test_save_and_load_filter(self):
        """Test saving and loading custom filters"""
        filter_config = {
            "type": "enhance",
            "brightness": 1.5,
            "contrast": 1.2
        }
        
        # Save filter
        filter_name = "test_filter"
        self.filter_system.save_filter(filter_name, filter_config)
        
        # Load filter
        loaded_config = self.filter_system.load_filter(filter_name)
        
        self.assertEqual(loaded_config, filter_config)
        
        # Check it appears in saved filters list
        saved_filters = self.filter_system.list_saved_filters()
        self.assertIn(filter_name, saved_filters)
    
    def test_apply_filter_to_image_file(self):
        """Test applying filter to image file"""
        output_path = os.path.join(self.temp_dir, "filtered.png")
        
        success, message = self.filter_system.apply_filter_to_image(
            self.test_image_path, output_path, "Grayscale"
        )
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        self.assertIn("Applied", message)
    
    def test_batch_apply_filter(self):
        """Test batch filter application"""
        # Create input folder with multiple images
        input_folder = os.path.join(self.temp_dir, "input")
        output_folder = os.path.join(self.temp_dir, "output")
        os.makedirs(input_folder)
        
        # Create test images
        for i in range(3):
            img = Image.new('RGB', (50, 50), (i*80, 100, 200))
            img.save(os.path.join(input_folder, f"test_{i}.png"))
        
        # Apply filter to batch
        results = self.filter_system.batch_apply_filter(
            input_folder, output_folder, "Blur"
        )
        
        # Verify results
        self.assertEqual(len(results), 3)
        self.assertTrue(all(success for success, _ in results))
        self.assertTrue(os.path.exists(output_folder))

class TestBatchImageProcessor(unittest.TestCase):
    """Test the BatchImageProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = BatchImageProcessor()
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test images
        self.input_folder = os.path.join(self.temp_dir, "input")
        os.makedirs(self.input_folder)
        
        for i in range(2):
            img = Image.new('RGB', (100, 100), (i*127, 127, 255-i*127))
            img.save(os.path.join(self.input_folder, f"test_{i}.png"))
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_format_conversion_operation(self):
        """Test format conversion operation"""
        output_folder = os.path.join(self.temp_dir, "output")
        operations = [
            {"type": "convert_format", "format": "JPEG", "quality": 90}
        ]
        
        results = self.processor.process_batch(
            self.input_folder, output_folder, operations
        )
        
        # Verify results
        self.assertEqual(len(results), 2)
        self.assertTrue(all(success for success, _ in results))
        
        # Check output files
        output_files = os.listdir(output_folder)
        self.assertEqual(len(output_files), 2)
        self.assertTrue(all(f.endswith('.jpg') for f in output_files))
    
    def test_filter_operation(self):
        """Test filter application operation"""
        output_folder = os.path.join(self.temp_dir, "output")
        operations = [
            {"type": "apply_filter", "filter": "Grayscale"}
        ]
        
        results = self.processor.process_batch(
            self.input_folder, output_folder, operations
        )
        
        # Verify results
        self.assertEqual(len(results), 2)
        self.assertTrue(all(success for success, _ in results))
    
    def test_chained_operations(self):
        """Test multiple chained operations"""
        output_folder = os.path.join(self.temp_dir, "output")
        operations = [
            {"type": "convert_format", "format": "JPEG", "quality": 95},
            {"type": "apply_filter", "filter": "Blur"}
        ]
        
        results = self.processor.process_batch(
            self.input_folder, output_folder, operations
        )
        
        # Verify results
        self.assertEqual(len(results), 2)
        self.assertTrue(all(success for success, _ in results))
        
        # Check that final output is JPEG (from first operation)
        output_files = os.listdir(output_folder)
        self.assertTrue(all(f.endswith('.jpg') for f in output_files))

@unittest.skipIf(not RAW_CONVERTER_AVAILABLE, "rawpy not available")
class TestRawConverter(unittest.TestCase):
    """Test the RawConverter class (if rawpy is available)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.converter = RawConverter()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_is_raw_file(self):
        """Test RAW file detection"""
        self.assertTrue(self.converter.is_raw_file("test.arw"))
        self.assertTrue(self.converter.is_raw_file("test.cr2"))
        self.assertTrue(self.converter.is_raw_file("test.nef"))
        self.assertFalse(self.converter.is_raw_file("test.jpg"))
        self.assertFalse(self.converter.is_raw_file("test.png"))

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)
    
    def test_filter_system_integration(self):
        """Test that filter system integrates properly"""
        filter_system = ImageFilterSystem()
        
        # Test that all built-in filters can be retrieved
        all_filters = filter_system.get_all_filters()
        self.assertGreater(len(all_filters), 0)
        
        # Test that built-in filters are included
        self.assertIn("Blur", all_filters)
        self.assertIn("Vintage", all_filters)
    
    def test_batch_processor_with_real_filters(self):
        """Test batch processor with actual filter system"""
        # Create test image
        input_folder = os.path.join(self.temp_dir, "input")
        output_folder = os.path.join(self.temp_dir, "output")
        os.makedirs(input_folder)
        
        img = Image.new('RGB', (100, 100), (255, 128, 0))
        img.save(os.path.join(input_folder, "test.png"))
        
        # Create processor and run with filter
        processor = BatchImageProcessor()
        operations = [{"type": "apply_filter", "filter": "Sepia"}]
        
        results = processor.process_batch(input_folder, output_folder, operations)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0][0])  # Success

def run_tests():
    """Run all tests and return results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestImageConverter,
        TestImageFilterSystem, 
        TestBatchImageProcessor,
        TestIntegration
    ]
    
    if RAW_CONVERTER_AVAILABLE:
        test_classes.append(TestRawConverter)
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    return result

if __name__ == "__main__":
    print("Running comprehensive tests for image processing scripts...")
    print("=" * 60)
    
    result = run_tests()
    
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
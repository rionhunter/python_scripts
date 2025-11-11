#!/usr/bin/env python3
"""
Master test runner for all image processing tests
Runs all test suites and generates a comprehensive report
"""

import sys
import os
import time
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_all_tests():
    """Run all test suites and generate report"""
    print("🧪 IMAGE PROCESSING TOOLKIT - COMPREHENSIVE TEST REPORT")
    print("=" * 70)
    
    start_time = time.time()
    
    # Test 1: Core functionality tests
    print("\n📋 RUNNING CORE FUNCTIONALITY TESTS")
    print("-" * 50)
    
    try:
        from test_image_processing import run_tests
        core_result = run_tests()
        core_success = core_result.wasSuccessful()
        core_tests = core_result.testsRun
        core_failures = len(core_result.failures)
        core_errors = len(core_result.errors)
    except Exception as e:
        print(f"❌ Core tests failed to run: {e}")
        core_success = False
        core_tests = 0
        core_failures = 1
        core_errors = 0
    
    # Test 2: Edge cases and robustness tests
    print("\n🔍 RUNNING EDGE CASE AND ROBUSTNESS TESTS")
    print("-" * 50)
    
    try:
        from test_edge_cases import run_edge_case_tests
        edge_result = run_edge_case_tests()
        edge_success = edge_result.wasSuccessful()
        edge_tests = edge_result.testsRun
        edge_failures = len(edge_result.failures)
        edge_errors = len(edge_result.errors)
    except Exception as e:
        print(f"❌ Edge case tests failed to run: {e}")
        edge_success = False
        edge_tests = 0
        edge_failures = 1
        edge_errors = 0
    
    # Test 3: Import and basic functionality tests
    print("\n🔧 RUNNING IMPORT AND BASIC FUNCTIONALITY TESTS")
    print("-" * 50)
    
    import_tests = 0
    import_failures = 0
    
    modules_to_test = [
        ("raw_converter", "RawConverter"),
        ("image_converter", "ImageConverter"), 
        ("image_filter_system", "ImageFilterSystem"),
        ("batch_image_processor", "BatchImageProcessor"),
        ("image_toolkit_launcher", None)  # Just import, no class
    ]
    
    for module_name, class_name in modules_to_test:
        import_tests += 1
        try:
            module = __import__(module_name)
            if class_name:
                cls = getattr(module, class_name)
                # Try to instantiate
                instance = cls()
                print(f"✅ {module_name}.{class_name} - OK")
            else:
                print(f"✅ {module_name} - OK")
        except Exception as e:
            print(f"❌ {module_name} - FAILED: {e}")
            import_failures += 1
    
    import_success = import_failures == 0
    
    # Test 4: File and dependency checks
    print("\n📁 RUNNING FILE AND DEPENDENCY CHECKS")
    print("-" * 50)
    
    file_tests = 0
    file_failures = 0
    
    required_files = [
        "raw_converter.py",
        "image_converter.py", 
        "image_filter_system.py",
        "batch_image_processor.py",
        "image_toolkit_launcher.py",
        "requirements.txt",
        "README_image_processing.md"
    ]
    
    for filename in required_files:
        file_tests += 1
        if os.path.exists(filename):
            print(f"✅ {filename} - EXISTS")
        else:
            print(f"❌ {filename} - MISSING")
            file_failures += 1
    
    # Check dependencies
    file_tests += 1
    try:
        import PIL
        import rawpy
        import imageio
        import numpy
        print("✅ All required dependencies - INSTALLED")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        file_failures += 1
    
    file_success = file_failures == 0
    
    # Generate final report
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n" + "=" * 70)
    print("📊 FINAL TEST REPORT")
    print("=" * 70)
    
    total_tests = core_tests + edge_tests + import_tests + file_tests
    total_failures = core_failures + edge_failures + import_failures + file_failures
    total_errors = core_errors + edge_errors
    
    print(f"⏱️  Total execution time: {total_time:.2f} seconds")
    print(f"🧪 Total tests run: {total_tests}")
    print(f"✅ Successful tests: {total_tests - total_failures - total_errors}")
    print(f"❌ Failed tests: {total_failures}")
    print(f"🚨 Error tests: {total_errors}")
    print()
    
    # Test suite breakdown
    print("📋 Test Suite Breakdown:")
    print(f"   Core Functionality: {core_tests} tests - {'✅ PASS' if core_success else '❌ FAIL'}")
    print(f"   Edge Cases: {edge_tests} tests - {'✅ PASS' if edge_success else '❌ FAIL'}")
    print(f"   Import Tests: {import_tests} tests - {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   File/Dependency: {file_tests} tests - {'✅ PASS' if file_success else '❌ FAIL'}")
    print()
    
    # Overall status
    overall_success = core_success and edge_success and import_success and file_success
    
    if overall_success:
        print("🎉 OVERALL STATUS: ALL TESTS PASSED!")
        print("✨ The image processing toolkit is ready for use!")
    else:
        print("⚠️  OVERALL STATUS: SOME ISSUES FOUND")
        print("🔧 Please review the failed tests above")
    
    print("\n" + "=" * 70)
    print("📚 TOOLKIT SUMMARY")
    print("=" * 70)
    print("🖼️  Image Processing Toolkit Features:")
    print("   • RAW file conversion (ARW, CR2, NEF, etc.)")
    print("   • Format conversion (JPEG, PNG, WEBP, TIFF, etc.)")
    print("   • Custom filter system with 13+ presets")
    print("   • Batch processing with operation chaining")
    print("   • GUI and command-line interfaces")
    print("   • Comprehensive error handling")
    print("   • Memory-efficient processing")
    
    print("\n🚀 Quick Start:")
    print("   python image_toolkit_launcher.py  # Launch main GUI")
    print("   python raw_converter.py           # RAW conversion")
    print("   python image_filter_system.py     # Filter editor")
    print("   python batch_image_processor.py   # Advanced workflows")
    
    return overall_success

if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)
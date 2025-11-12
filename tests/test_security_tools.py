import unittest
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from security.hash_tool import calculate_hash, verify_hash, calculate_multiple_hashes
from security.password_tool import generate_password, check_password_strength


class TestHashTool(unittest.TestCase):
    def setUp(self):
        """Create a temporary test file."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.write("test content for hashing")
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up temporary file."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_calculate_hash_sha256(self):
        """Test SHA-256 hash calculation."""
        hash_value = calculate_hash(self.temp_file.name, 'sha256')
        self.assertEqual(len(hash_value), 64)  # SHA-256 produces 64 hex chars
        self.assertIsInstance(hash_value, str)
    
    def test_calculate_hash_md5(self):
        """Test MD5 hash calculation."""
        hash_value = calculate_hash(self.temp_file.name, 'md5')
        self.assertEqual(len(hash_value), 32)  # MD5 produces 32 hex chars
    
    def test_verify_hash(self):
        """Test hash verification."""
        expected_hash = calculate_hash(self.temp_file.name, 'sha256')
        self.assertTrue(verify_hash(self.temp_file.name, expected_hash, 'sha256'))
        self.assertFalse(verify_hash(self.temp_file.name, 'wrong_hash', 'sha256'))
    
    def test_calculate_multiple_hashes(self):
        """Test multiple hash calculation."""
        algorithms = ['md5', 'sha1', 'sha256']
        hashes = calculate_multiple_hashes(self.temp_file.name, algorithms)
        self.assertEqual(len(hashes), 3)
        self.assertIn('md5', hashes)
        self.assertIn('sha1', hashes)
        self.assertIn('sha256', hashes)


class TestPasswordTool(unittest.TestCase):
    def test_generate_password_default(self):
        """Test default password generation."""
        password = generate_password()
        self.assertEqual(len(password), 16)
        self.assertIsInstance(password, str)
    
    def test_generate_password_custom_length(self):
        """Test custom length password."""
        password = generate_password(length=20)
        self.assertEqual(len(password), 20)
    
    def test_generate_password_no_special(self):
        """Test password without special characters."""
        password = generate_password(length=10, use_special=False)
        self.assertEqual(len(password), 10)
        # Check no special chars
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        self.assertFalse(any(c in special_chars for c in password))
    
    def test_check_password_strength_weak(self):
        """Test weak password detection."""
        strength, score, criteria = check_password_strength("123")
        self.assertIn(strength, ["Very Weak", "Weak"])
        self.assertLess(score, 40)
    
    def test_check_password_strength_strong(self):
        """Test strong password detection."""
        strength, score, criteria = check_password_strength("MyStr0ng!Pass123")
        self.assertIn(strength, ["Strong", "Very Strong"])
        self.assertGreater(score, 60)
        self.assertTrue(criteria['length'])
        self.assertTrue(criteria['uppercase'])
        self.assertTrue(criteria['lowercase'])
        self.assertTrue(criteria['digits'])
        self.assertTrue(criteria['special'])


if __name__ == '__main__':
    unittest.main()

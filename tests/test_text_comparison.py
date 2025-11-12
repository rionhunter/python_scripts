import unittest
import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from text_comparison.similarity_tool import (
    jaccard_similarity, cosine_similarity, levenshtein_distance,
    word_overlap_similarity, tokenize
)


class TestSimilarityTool(unittest.TestCase):
    def test_jaccard_similarity_identical(self):
        """Test Jaccard similarity with identical sets."""
        set1 = {1, 2, 3, 4, 5}
        set2 = {1, 2, 3, 4, 5}
        similarity = jaccard_similarity(set1, set2)
        self.assertEqual(similarity, 1.0)
    
    def test_jaccard_similarity_different(self):
        """Test Jaccard similarity with different sets."""
        set1 = {1, 2, 3}
        set2 = {4, 5, 6}
        similarity = jaccard_similarity(set1, set2)
        self.assertEqual(similarity, 0.0)
    
    def test_jaccard_similarity_partial(self):
        """Test Jaccard similarity with partial overlap."""
        set1 = {1, 2, 3, 4}
        set2 = {3, 4, 5, 6}
        similarity = jaccard_similarity(set1, set2)
        self.assertEqual(similarity, 1/3)  # 2 common, 6 total
    
    def test_cosine_similarity_identical(self):
        """Test cosine similarity with identical vectors."""
        vec1 = {'a': 1, 'b': 2, 'c': 3}
        vec2 = {'a': 1, 'b': 2, 'c': 3}
        similarity = cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 1.0, places=5)
    
    def test_cosine_similarity_different(self):
        """Test cosine similarity with orthogonal vectors."""
        vec1 = {'a': 1}
        vec2 = {'b': 1}
        similarity = cosine_similarity(vec1, vec2)
        self.assertEqual(similarity, 0.0)
    
    def test_levenshtein_distance_identical(self):
        """Test Levenshtein distance with identical strings."""
        distance = levenshtein_distance("hello", "hello")
        self.assertEqual(distance, 0)
    
    def test_levenshtein_distance_different(self):
        """Test Levenshtein distance with different strings."""
        distance = levenshtein_distance("kitten", "sitting")
        self.assertEqual(distance, 3)  # 3 edits needed
    
    def test_word_overlap_similarity(self):
        """Test word overlap similarity."""
        text1 = "the quick brown fox"
        text2 = "the fast brown dog"
        similarity = word_overlap_similarity(text1, text2)
        self.assertGreater(similarity, 0.0)
        self.assertLess(similarity, 1.0)
    
    def test_tokenize(self):
        """Test word tokenization."""
        text = "Hello, World! This is a test."
        tokens = tokenize(text)
        self.assertEqual(tokens, ['hello', 'world', 'this', 'is', 'a', 'test'])


class TestDiffTool(unittest.TestCase):
    def setUp(self):
        """Create temporary test files."""
        self.temp_file1 = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file1.write("line 1\nline 2\nline 3\n")
        self.temp_file1.close()
        
        self.temp_file2 = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file2.write("line 1\nline 2 modified\nline 3\nline 4\n")
        self.temp_file2.close()
    
    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_file1.name):
            os.unlink(self.temp_file1.name)
        if os.path.exists(self.temp_file2.name):
            os.unlink(self.temp_file2.name)
    
    def test_files_created(self):
        """Test that temporary files were created."""
        self.assertTrue(os.path.exists(self.temp_file1.name))
        self.assertTrue(os.path.exists(self.temp_file2.name))


if __name__ == '__main__':
    unittest.main()

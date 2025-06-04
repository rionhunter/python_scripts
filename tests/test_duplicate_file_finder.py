import os
import tempfile
import unittest
from duplicate_file_finder import hash_file, find_duplicates

class TestDuplicateFileFinder(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.dir = self.tempdir.name
        # create duplicate files
        with open(os.path.join(self.dir, 'a.txt'), 'w') as f:
            f.write('hello')
        with open(os.path.join(self.dir, 'b.txt'), 'w') as f:
            f.write('hello')
        with open(os.path.join(self.dir, 'c.txt'), 'w') as f:
            f.write('world')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_hash_file(self):
        path = os.path.join(self.dir, 'a.txt')
        self.assertEqual(hash_file(path), hash_file(path))

    def test_find_duplicates(self):
        duplicates = find_duplicates(self.dir)
        # Expect one group with two files
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(len(duplicates[0]), 2)

if __name__ == '__main__':
    unittest.main()

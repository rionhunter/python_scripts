import os
import tempfile
import unittest
from utils.file_utils.find_large_files import find_large_files

class TestFindLargeFiles(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.dir = self.tempdir.name
        with open(os.path.join(self.dir, 'small.txt'), 'w') as f:
            f.write('hi')
        with open(os.path.join(self.dir, 'big.txt'), 'w') as f:
            f.write('a' * 1024)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_find_large_files(self):
        large = find_large_files(self.dir, 100)
        self.assertEqual(len(large), 1)
        self.assertTrue(large[0].endswith('big.txt'))

if __name__ == '__main__':
    unittest.main()

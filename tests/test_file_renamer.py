import os
import tempfile
import unittest
from utils.file_utils.file_renamer import rename_files

class TestFileRenamer(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.dir = self.tempdir.name
        for name in ['x.txt', 'y.txt', 'z.txt']:
            open(os.path.join(self.dir, name), 'w').close()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_rename_files(self):
        renamed = rename_files(self.dir, 'file', '.txt')
        expected = [os.path.join(self.dir, f'file{i}.txt') for i in range(1, 4)]
        self.assertEqual(renamed, expected)
        for path in expected:
            self.assertTrue(os.path.exists(path))

if __name__ == '__main__':
    unittest.main()

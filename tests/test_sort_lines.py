import unittest
from sort_lines import sort_lines

class TestSortLines(unittest.TestCase):
    def test_sort_lines(self):
        text = 'b\na\nc'
        self.assertEqual(sort_lines(text), 'a\nb\nc')

if __name__ == '__main__':
    unittest.main()

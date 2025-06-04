import unittest
from tabs_to_spaces import tabs_to_spaces
from spaces_to_tabs import spaces_to_tabs

class TestTabSpaceConversion(unittest.TestCase):
    def test_tabs_to_spaces(self):
        self.assertEqual(tabs_to_spaces('\tfoo', 2), '  foo')

    def test_spaces_to_tabs(self):
        self.assertEqual(spaces_to_tabs('    foo', 4), '\tfoo')

if __name__ == '__main__':
    unittest.main()

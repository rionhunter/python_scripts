import unittest
from lines_to_csv import lines_to_csv_string

class TestLinesToCsv(unittest.TestCase):
    def test_lines_to_csv(self):
        result = lines_to_csv_string(['a', 'b'])
        self.assertEqual(result.strip(), 'a\nb')

if __name__ == '__main__':
    unittest.main()

import json
import unittest
from json_pretty_printer import pretty_json

class TestJsonPrettyPrinter(unittest.TestCase):
    def test_pretty_json(self):
        data = {"b": 1, "a": 2}
        pretty = pretty_json(data)
        self.assertEqual(json.loads(pretty), data)
        self.assertIn('\n', pretty)

if __name__ == '__main__':
    unittest.main()

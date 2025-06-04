import unittest
from word_counter import count_words

class TestWordCounter(unittest.TestCase):
    def test_count_words(self):
        self.assertEqual(count_words('Hello world'), 2)
        self.assertEqual(count_words('One\ntwo\nthree'), 3)

if __name__ == '__main__':
    unittest.main()

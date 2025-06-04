import unittest
from extract_emails import extract_emails

class TestExtractEmails(unittest.TestCase):
    def test_extract_emails(self):
        text = 'Contact a@b.com and c@d.org.'
        self.assertEqual(extract_emails(text), ['a@b.com', 'c@d.org'])

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Extract email addresses from text or file."""
import argparse
import re
from typing import List


def extract_emails(text: str) -> List[str]:
    """Return list of email addresses found in text."""
    return re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)


def read_text(source: str) -> str:
    try:
        with open(source, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return source


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract emails")
    parser.add_argument("source", help="File path or text")
    args = parser.parse_args()
    print('\n'.join(extract_emails(read_text(args.source))))

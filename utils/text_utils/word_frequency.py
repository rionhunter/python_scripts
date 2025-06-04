#!/usr/bin/env python3
"""Display word frequency counts."""
import argparse
import re
from collections import Counter

def word_frequency(text: str) -> Counter:
    words = re.findall(r"\b\w+\b", text.lower())
    return Counter(words)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Word frequency")
    parser.add_argument("source", help="File path or text")
    args = parser.parse_args()
    try:
        with open(args.source, 'r') as f:
            text = f.read()
    except FileNotFoundError:
        text = args.source
    for word, count in word_frequency(text).items():
        print(f"{word}: {count}")

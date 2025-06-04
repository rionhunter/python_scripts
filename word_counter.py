#!/usr/bin/env python3
"""Count words in a string or file."""
import argparse
import re
from typing import Iterable


def count_words(text: str) -> int:
    """Return the number of words in *text*."""
    return len(re.findall(r"\b\w+\b", text))


def read_text(source: str) -> str:
    """Return the content of a file or the string itself if file not found."""
    try:
        with open(source, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return source


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count words")
    parser.add_argument("source", help="File path or text")
    args = parser.parse_args()
    text = read_text(args.source)
    print(count_words(text))

#!/usr/bin/env python3
"""Count lines in text or a file."""
import argparse

def count_lines(text: str) -> int:
    return len(text.splitlines())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count lines")
    parser.add_argument("source", help="File path or text")
    args = parser.parse_args()
    try:
        with open(args.source, 'r') as f:
            data = f.read()
        print(count_lines(data))
    except FileNotFoundError:
        print(count_lines(args.source))

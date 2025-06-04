#!/usr/bin/env python3
"""Sort lines in a text file or string."""
import argparse


def sort_lines(text: str) -> str:
    """Return the lines of *text* sorted alphabetically."""
    return '\n'.join(sorted(text.splitlines()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort lines")
    parser.add_argument("source", help="File path or text")
    args = parser.parse_args()
    try:
        with open(args.source, 'r') as f:
            content = f.read()
        sorted_content = sort_lines(content)
        with open(args.source, 'w') as f:
            f.write(sorted_content)
    except FileNotFoundError:
        print(sort_lines(args.source))

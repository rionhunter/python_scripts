#!/usr/bin/env python3
"""Convert groups of spaces to tabs in a text string."""
import argparse


def spaces_to_tabs(text: str, spaces: int = 4) -> str:
    """Replace sequences of *spaces* spaces with a TAB."""
    return text.replace(' ' * spaces, '\t')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert spaces to tabs")
    parser.add_argument("source", help="File path or text")
    parser.add_argument("-s", "--spaces", type=int, default=4, help="Number of spaces that represent a tab")
    args = parser.parse_args()
    try:
        with open(args.source, 'r') as f:
            data = f.read()
        converted = spaces_to_tabs(data, args.spaces)
        with open(args.source, 'w') as f:
            f.write(converted)
    except FileNotFoundError:
        print(spaces_to_tabs(args.source, args.spaces))

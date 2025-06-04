#!/usr/bin/env python3
"""Convert tabs to spaces in a text string."""
import argparse


def tabs_to_spaces(text: str, spaces: int = 4) -> str:
    """Replace TAB characters with *spaces* number of spaces."""
    return text.replace('\t', ' ' * spaces)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert tabs to spaces")
    parser.add_argument("source", help="File path or text")
    parser.add_argument("-s", "--spaces", type=int, default=4, help="Number of spaces")
    args = parser.parse_args()
    try:
        with open(args.source, 'r') as f:
            data = f.read()
        converted = tabs_to_spaces(data, args.spaces)
        with open(args.source, 'w') as f:
            f.write(converted)
    except FileNotFoundError:
        print(tabs_to_spaces(args.source, args.spaces))

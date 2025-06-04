#!/usr/bin/env python3
"""Remove duplicate lines preserving order."""
import argparse

def deduplicate_lines(text: str) -> str:
    seen = set()
    result = []
    for line in text.splitlines():
        if line not in seen:
            seen.add(line)
            result.append(line)
    return "\n".join(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove duplicate lines")
    parser.add_argument("source", help="File path or text")
    args = parser.parse_args()
    try:
        with open(args.source, 'r') as f:
            data = f.read()
        out = deduplicate_lines(data)
        with open(args.source, 'w') as f:
            f.write(out)
    except FileNotFoundError:
        print(deduplicate_lines(args.source))

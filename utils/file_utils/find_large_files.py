#!/usr/bin/env python3
"""List files larger than a given size."""
import argparse
import os
from typing import List


def find_large_files(directory: str, size: int) -> List[str]:
    """Return file paths in *directory* larger than *size* bytes."""
    large = []
    for root, _dirs, files in os.walk(directory):
        for name in files:
            path = os.path.join(root, name)
            if os.path.getsize(path) > size:
                large.append(path)
    return large


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find large files")
    parser.add_argument("directory")
    parser.add_argument("size", type=int, help="Size in bytes")
    args = parser.parse_args()
    for path in find_large_files(args.directory, args.size):
        print(path)

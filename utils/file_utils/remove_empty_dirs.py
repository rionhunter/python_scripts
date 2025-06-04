#!/usr/bin/env python3
"""Remove empty directories recursively."""
import argparse
import os
from typing import List

def remove_empty_dirs(path: str) -> List[str]:
    removed = []
    for root, dirs, files in os.walk(path, topdown=False):
        for d in dirs:
            full = os.path.join(root, d)
            if not os.listdir(full):
                os.rmdir(full)
                removed.append(full)
    return removed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove empty directories")
    parser.add_argument("path")
    args = parser.parse_args()
    for d in remove_empty_dirs(args.path):
        print(d)

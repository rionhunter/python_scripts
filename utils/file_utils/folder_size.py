#!/usr/bin/env python3
"""Calculate total size of a folder."""
import argparse
import os

def folder_size(path: str) -> int:
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            total += os.path.getsize(os.path.join(root, name))
    return total

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Folder size in bytes")
    parser.add_argument("path")
    args = parser.parse_args()
    print(folder_size(args.path))

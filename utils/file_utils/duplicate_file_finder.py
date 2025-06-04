#!/usr/bin/env python3
"""Find duplicate files in a directory using MD5 hashes."""
import hashlib
import os
from typing import Dict, List

def hash_file(path: str, chunk_size: int = 8192) -> str:
    """Return the MD5 hash of a file."""
    md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

def find_duplicates(directory: str) -> List[List[str]]:
    """Return groups of duplicate file paths found under *directory*."""
    hashes: Dict[str, List[str]] = {}
    for root, _dirs, files in os.walk(directory):
        for name in files:
            path = os.path.join(root, name)
            file_hash = hash_file(path)
            hashes.setdefault(file_hash, []).append(path)
    return [paths for paths in hashes.values() if len(paths) > 1]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find duplicate files")
    parser.add_argument("directory", help="Directory to scan")
    args = parser.parse_args()
    dupes = find_duplicates(args.directory)
    for group in dupes:
        print("Duplicate group:")
        for path in group:
            print("  ", path)

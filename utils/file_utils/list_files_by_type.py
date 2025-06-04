#!/usr/bin/env python3
"""List files of a given extension."""
import argparse
import os
from typing import List

def list_files_by_type(directory: str, extension: str) -> List[str]:
    matches = []
    for root, _dirs, files in os.walk(directory):
        for name in files:
            if name.endswith(extension):
                matches.append(os.path.join(root, name))
    return matches

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List files by type")
    parser.add_argument("directory")
    parser.add_argument("extension")
    args = parser.parse_args()
    for path in list_files_by_type(args.directory, args.extension):
        print(path)

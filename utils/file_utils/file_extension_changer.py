#!/usr/bin/env python3
"""Change file extensions in a directory."""
import argparse
import os
from typing import List

def change_extension(directory: str, old_ext: str, new_ext: str) -> List[str]:
    changed = []
    for root, _dirs, files in os.walk(directory):
        for name in files:
            if name.endswith(old_ext):
                base = name[:-len(old_ext)]
                new_name = base + new_ext
                os.rename(os.path.join(root, name), os.path.join(root, new_name))
                changed.append(os.path.join(root, new_name))
    return changed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Change file extensions")
    parser.add_argument("directory")
    parser.add_argument("old_ext")
    parser.add_argument("new_ext")
    args = parser.parse_args()
    for path in change_extension(args.directory, args.old_ext, args.new_ext):
        print(path)

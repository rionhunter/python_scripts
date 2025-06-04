#!/usr/bin/env python3
"""Rename files of a given type sequentially with a prefix."""
import os
from typing import List

def rename_files(directory: str, prefix: str, filetype: str) -> List[str]:
    """Rename files and return new file paths."""
    renamed = []
    i = 1
    for name in sorted(os.listdir(directory)):
        if name.endswith(filetype):
            new_name = f"{prefix}{i}{filetype}"
            src = os.path.join(directory, name)
            dst = os.path.join(directory, new_name)
            os.rename(src, dst)
            renamed.append(dst)
            i += 1
    return renamed

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Rename files sequentially")
    parser.add_argument("directory")
    parser.add_argument("prefix")
    parser.add_argument("filetype")
    args = parser.parse_args()
    for path in rename_files(args.directory, args.prefix, args.filetype):
        print(path)

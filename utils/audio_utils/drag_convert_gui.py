#!/usr/bin/env python3
"""GUI helper to convert audio files to MP3 using ffmpeg.

Files can be provided on the command line (e.g. dragging onto the script)
or selected through a file dialog.
"""
import argparse
import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from typing import List


def convert_to_mp3(path: str) -> List[str]:
    """Return the ffmpeg command to convert *path* to an MP3 next to it."""
    base, _ = os.path.splitext(path)
    output = base + ".mp3"
    return ["ffmpeg", "-i", path, output]


def run_conversion(paths: List[str]) -> None:
    for p in paths:
        cmd = convert_to_mp3(p)
        subprocess.run(cmd, check=True)


def select_files() -> List[str]:
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames(title="Select audio files")
    root.update()
    root.destroy()
    return list(files)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert audio files to MP3")
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()
    files = args.files or select_files()
    if files:
        run_conversion(list(files))


if __name__ == "__main__":
    main()

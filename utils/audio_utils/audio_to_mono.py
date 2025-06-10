#!/usr/bin/env python3
"""Create an ffmpeg command to convert audio to mono."""
import argparse
import subprocess
from typing import List


def to_mono_command(input_file: str, output_file: str) -> List[str]:
    """Return the ffmpeg command to convert audio to mono."""
    return [
        "ffmpeg",
        "-i",
        input_file,
        "-ac",
        "1",
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert audio to mono")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    args = parser.parse_args()
    cmd = to_mono_command(args.input_file, args.output_file)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create an ffmpeg command to reverse an audio file."""
import argparse
import subprocess
from typing import List


def reverse_command(input_file: str, output_file: str) -> List[str]:
    """Return the ffmpeg command to reverse *input_file*."""
    return [
        "ffmpeg",
        "-i",
        input_file,
        "-filter:a",
        "areverse",
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Reverse audio")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    args = parser.parse_args()
    cmd = reverse_command(args.input_file, args.output_file)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

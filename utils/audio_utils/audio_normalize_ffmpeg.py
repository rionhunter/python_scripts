#!/usr/bin/env python3
"""Create an ffmpeg command to normalize audio loudness."""
import argparse
import subprocess
from typing import List


def normalize_command(input_file: str, output_file: str) -> List[str]:
    """Return the ffmpeg command to normalize audio using loudnorm."""
    return [
        "ffmpeg",
        "-i",
        input_file,
        "-filter:a",
        "loudnorm",
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize audio loudness")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    args = parser.parse_args()
    cmd = normalize_command(args.input_file, args.output_file)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create an ffmpeg command to extract a portion of an audio file."""
import argparse
import subprocess
from typing import List


def split_command(input_file: str, start: float, duration: float, output_file: str) -> List[str]:
    """Return the ffmpeg command to slice the audio."""
    return [
        "ffmpeg",
        "-ss",
        str(start),
        "-t",
        str(duration),
        "-i",
        input_file,
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract part of an audio file")
    parser.add_argument("input_file")
    parser.add_argument("start", type=float)
    parser.add_argument("duration", type=float)
    parser.add_argument("output_file")
    args = parser.parse_args()
    cmd = split_command(args.input_file, args.start, args.duration, args.output_file)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

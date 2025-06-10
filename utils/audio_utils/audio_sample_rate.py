#!/usr/bin/env python3
"""Create an ffmpeg command to change the sample rate of audio."""
import argparse
import subprocess
from typing import List


def sample_rate_command(input_file: str, output_file: str, rate: int) -> List[str]:
    """Return the ffmpeg command to resample audio."""
    return [
        "ffmpeg",
        "-i",
        input_file,
        "-ar",
        str(rate),
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Change audio sample rate")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("rate", type=int)
    args = parser.parse_args()
    cmd = sample_rate_command(args.input_file, args.output_file, args.rate)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

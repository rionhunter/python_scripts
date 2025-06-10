#!/usr/bin/env python3
"""Create an ffmpeg command to record from the default microphone."""
import argparse
import subprocess
from typing import List


def record_command(output_file: str, duration: int) -> List[str]:
    """Return the ffmpeg command to record audio."""
    return [
        "ffmpeg",
        "-f",
        "alsa",
        "-i",
        "default",
        "-t",
        str(duration),
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Record microphone")
    parser.add_argument("output_file")
    parser.add_argument("duration", type=int, help="Duration in seconds")
    args = parser.parse_args()
    cmd = record_command(args.output_file, args.duration)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

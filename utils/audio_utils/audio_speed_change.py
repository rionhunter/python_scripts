#!/usr/bin/env python3
"""Create an ffmpeg command to change audio playback speed."""
import argparse
import subprocess
from typing import List


def speed_change_command(input_file: str, output_file: str, speed: float) -> List[str]:
    """Return the ffmpeg command to change playback speed."""
    return [
        "ffmpeg",
        "-i",
        input_file,
        "-filter:a",
        f"atempo={speed}",
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Change audio playback speed")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("speed", type=float)
    args = parser.parse_args()
    cmd = speed_change_command(args.input_file, args.output_file, args.speed)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

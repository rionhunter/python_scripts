#!/usr/bin/env python3
"""Create an ffmpeg command to trim silence from start and end."""
import argparse
import subprocess
from typing import List


def trim_silence_command(input_file: str, output_file: str, threshold: str = '0.1') -> List[str]:
    """Return the ffmpeg command to remove silence using silenceremove filter."""
    filter_str = f"silenceremove=start_periods=1:start_threshold={threshold}:" \
                 f"detection=peak,end_periods=1:end_threshold={threshold}"
    return [
        "ffmpeg",
        "-i",
        input_file,
        "-af",
        filter_str,
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Trim silence from audio")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--threshold", default="0.1")
    args = parser.parse_args()
    cmd = trim_silence_command(args.input_file, args.output_file, args.threshold)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

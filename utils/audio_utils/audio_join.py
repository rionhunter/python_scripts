#!/usr/bin/env python3
"""Create an ffmpeg command to concatenate multiple audio files."""
import argparse
import subprocess
from typing import List


def join_command(inputs: List[str], output_file: str) -> List[str]:
    """Return the ffmpeg command using concat filter."""
    filter_str = f"concat=n={len(inputs)}:v=0:a=1"
    cmd = [
        "ffmpeg",
    ]
    for inp in inputs:
        cmd.extend(["-i", inp])
    cmd.extend(["-filter_complex", filter_str, output_file])
    return cmd


def main() -> None:
    parser = argparse.ArgumentParser(description="Join audio files")
    parser.add_argument("output_file")
    parser.add_argument("inputs", nargs='+')
    args = parser.parse_args()
    cmd = join_command(args.inputs, args.output_file)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create an ffmpeg command to apply fade in and fade out."""
import argparse
import subprocess
from typing import List


def fade_command(input_file: str, output_file: str, fade_in: float, fade_out: float) -> List[str]:
    """Return the ffmpeg command to apply fades."""
    filter_str = f"afade=t=in:st=0:d={fade_in},afade=t=out:st={fade_out}:d={fade_in}"
    return [
        "ffmpeg",
        "-i",
        input_file,
        "-filter:a",
        filter_str,
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply audio fades")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("fade_in", type=float)
    parser.add_argument("fade_out", type=float)
    args = parser.parse_args()
    cmd = fade_command(args.input_file, args.output_file, args.fade_in, args.fade_out)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

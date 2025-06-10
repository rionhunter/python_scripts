#!/usr/bin/env python3
"""Create an ffmpeg command to loop audio a given number of times."""
import argparse
import subprocess
from typing import List


def loop_command(input_file: str, output_file: str, count: int) -> List[str]:
    """Return the ffmpeg command to loop audio."""
    return [
        "ffmpeg",
        "-stream_loop",
        str(count - 1),
        "-i",
        input_file,
        "-c",
        "copy",
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Loop audio")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("count", type=int)
    args = parser.parse_args()
    cmd = loop_command(args.input_file, args.output_file, args.count)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

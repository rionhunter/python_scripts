#!/usr/bin/env python3
"""Create an ffmpeg command to extract a single channel from stereo audio."""
import argparse
import subprocess
from typing import List


def channel_command(input_file: str, channel: int, output_file: str) -> List[str]:
    """Return the ffmpeg command to extract left (0) or right (1) channel."""
    filter_str = f"channelsplit=channel_layout=stereo:channels={['FL','FR'][channel]}"
    return [
        "ffmpeg",
        "-i",
        input_file,
        "-filter_complex",
        filter_str,
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a single audio channel")
    parser.add_argument("input_file")
    parser.add_argument("channel", type=int, choices=[0, 1], help="0=left, 1=right")
    parser.add_argument("output_file")
    args = parser.parse_args()
    cmd = channel_command(args.input_file, args.channel, args.output_file)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

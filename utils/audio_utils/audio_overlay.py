#!/usr/bin/env python3
"""Create an ffmpeg command to overlay two audio files."""
import argparse
import subprocess
from typing import List


def overlay_command(base_file: str, overlay_file: str, output_file: str) -> List[str]:
    """Return the ffmpeg command to mix two audio files."""
    return [
        "ffmpeg",
        "-i",
        base_file,
        "-i",
        overlay_file,
        "-filter_complex",
        "amix=inputs=2:duration=first:dropout_transition=2",
        output_file,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Overlay two audio files")
    parser.add_argument("base_file")
    parser.add_argument("overlay_file")
    parser.add_argument("output_file")
    args = parser.parse_args()
    cmd = overlay_command(args.base_file, args.overlay_file, args.output_file)
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()

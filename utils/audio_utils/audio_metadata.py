#!/usr/bin/env python3
"""Read simple metadata from a WAV file."""
import argparse
import wave
from typing import Tuple


def get_wav_metadata(path: str) -> Tuple[int, int, float]:
    """Return (channels, sample_rate, duration_seconds)."""
    with wave.open(path, 'rb') as wf:
        channels = wf.getnchannels()
        rate = wf.getframerate()
        frames = wf.getnframes()
    duration = frames / float(rate)
    return channels, rate, duration


def main() -> None:
    parser = argparse.ArgumentParser(description="Show WAV metadata")
    parser.add_argument("path")
    args = parser.parse_args()
    channels, rate, dur = get_wav_metadata(args.path)
    print(f"Channels: {channels}\nRate: {rate}\nDuration: {dur:.2f}s")


if __name__ == "__main__":
    main()

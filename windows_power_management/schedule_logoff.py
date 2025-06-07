#!/usr/bin/env python3
"""Log off the current Windows user after a specified number of minutes."""
import argparse
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("minutes", type=int, help="Minutes until logoff")
    args = parser.parse_args()
    seconds = args.minutes * 60
    print(f"Logging off in {args.minutes} minute(s)...")
    time.sleep(seconds)
    subprocess.run(['shutdown', '-l'], check=True)


if __name__ == '__main__':
    main()

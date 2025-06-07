#!/usr/bin/env python3
"""Hibernate Windows after a specified number of minutes."""
import argparse
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("minutes", type=int, help="Minutes until hibernate")
    args = parser.parse_args()
    seconds = args.minutes * 60
    print(f"Hibernating in {args.minutes} minute(s)...")
    time.sleep(seconds)
    subprocess.run(['shutdown', '/h'], check=True)


if __name__ == '__main__':
    main()

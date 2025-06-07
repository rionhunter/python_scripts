#!/usr/bin/env python3
"""Schedule a Windows shutdown after a specified number of minutes."""
import argparse
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("minutes", type=int, help="Minutes until shutdown")
    args = parser.parse_args()
    seconds = args.minutes * 60
    subprocess.run(['shutdown', '-s', '-t', str(seconds)], check=True)
    print(f"Shutdown scheduled in {args.minutes} minute(s).")


if __name__ == "__main__":
    main()

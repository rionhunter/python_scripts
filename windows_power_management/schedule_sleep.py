#!/usr/bin/env python3
"""Put Windows to sleep after a specified number of minutes."""
import argparse
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("minutes", type=int, help="Minutes until sleep")
    args = parser.parse_args()
    seconds = args.minutes * 60
    print(f"Sleeping in {args.minutes} minute(s)...")
    time.sleep(seconds)
    subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], check=True)


if __name__ == '__main__':
    main()

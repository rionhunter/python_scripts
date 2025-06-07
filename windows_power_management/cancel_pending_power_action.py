#!/usr/bin/env python3
"""Cancel any scheduled Windows shutdown or restart."""
import subprocess


def main():
    subprocess.run(['shutdown', '-a'], check=True)
    print("Cancelled pending shutdown/restart actions.")


if __name__ == '__main__':
    main()

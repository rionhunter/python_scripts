#!/usr/bin/env python3
"""List available Windows power plans."""
import subprocess


def main():
    result = subprocess.run(['powercfg', '/list'], capture_output=True, text=True, check=True)
    print(result.stdout)


if __name__ == '__main__':
    main()

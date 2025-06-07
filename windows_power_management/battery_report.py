#!/usr/bin/env python3
"""Generate a Windows battery report and print the file location."""
import subprocess
import os


def main():
    result = subprocess.run(['powercfg', '/batteryreport'], capture_output=True, text=True, check=True)
    for line in result.stdout.splitlines():
        if 'Battery life report saved to' in line:
            path = line.split('to')[-1].strip()
            print(f'Report saved to: {path}')
            break
    else:
        print(result.stdout)


if __name__ == '__main__':
    main()

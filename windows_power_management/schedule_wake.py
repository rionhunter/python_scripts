#!/usr/bin/env python3
"""Schedule a wake/boot time using Windows Task Scheduler."""
import argparse
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('time', help='Wake time in HH:MM format (24-hour)')
    parser.add_argument('--task-name', default='WakeFromSleep', help='Scheduled task name')
    args = parser.parse_args()

    cmd = [
        'schtasks', '/create', '/sc', 'once', '/tn', args.task_name,
        '/tr', 'cmd /c exit', '/st', args.time, '/ru', 'SYSTEM', '/RL', 'HIGHEST', '/F'
    ]
    subprocess.run(cmd, check=True)
    subprocess.run(['powercfg', '/waketimers'], check=True)
    print(f"Wake task '{args.task_name}' set for {args.time}.")


if __name__ == '__main__':
    main()

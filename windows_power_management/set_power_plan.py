#!/usr/bin/env python3
"""Switch the active Windows power plan.

Provide either a power plan GUID or a common plan name
('balanced', 'high_performance', 'power_saver').
"""
import argparse
import subprocess

# Built-in Windows power plan GUIDs
PLAN_GUIDS = {
    'balanced': '381b4222-f694-41f0-9685-ff5bb260df2e',
    'high_performance': '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',
    'power_saver': 'a1841308-3541-4fab-bc81-f71556f20b4a',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', help='Power plan name or GUID')
    args = parser.parse_args()

    guid = PLAN_GUIDS.get(args.plan.lower(), args.plan)
    subprocess.run(['powercfg', '/setactive', guid], check=True)
    print(f"Active power plan set to {args.plan} ({guid}).")


if __name__ == '__main__':
    main()

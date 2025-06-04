#!/usr/bin/env python3
"""Pretty print JSON from a file or string."""
import argparse
import json
from typing import Any


def pretty_json(data: Any) -> str:
    """Return data formatted with indentation and sorted keys."""
    return json.dumps(data, indent=2, sort_keys=True)


def read_json(path_or_string: str) -> Any:
    """Load JSON from file if path exists; otherwise parse the string."""
    try:
        with open(path_or_string, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return json.loads(path_or_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pretty print JSON")
    parser.add_argument("source", help="JSON file path or raw JSON string")
    args = parser.parse_args()
    data = read_json(args.source)
    print(pretty_json(data))

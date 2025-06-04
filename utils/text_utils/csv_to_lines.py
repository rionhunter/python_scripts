#!/usr/bin/env python3
"""Convert CSV text to newline-separated lines."""
import argparse
import csv
import io

def csv_to_lines(csv_text: str) -> str:
    reader = csv.reader(io.StringIO(csv_text))
    return "\n".join(row[0] for row in reader if row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSV to lines")
    parser.add_argument("source", help="File path or CSV text")
    args = parser.parse_args()
    try:
        with open(args.source, 'r') as f:
            data = f.read()
        result = csv_to_lines(data)
        with open(args.source, 'w') as f:
            f.write(result)
    except FileNotFoundError:
        print(csv_to_lines(args.source))

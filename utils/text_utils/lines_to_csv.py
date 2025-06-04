#!/usr/bin/env python3
"""Convert newline-separated values to CSV format."""
import argparse
import csv
import io


def lines_to_csv_string(lines):
    """Return CSV formatted string from an iterable of lines."""
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')
    for line in lines:
        writer.writerow([line])
    return output.getvalue()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert lines to CSV")
    parser.add_argument("source", help="File path or text")
    args = parser.parse_args()
    try:
        with open(args.source, 'r') as f:
            text = f.read()
        csv_text = lines_to_csv_string(text.splitlines())
        with open(args.source, 'w') as f:
            f.write(csv_text)
    except FileNotFoundError:
        print(lines_to_csv_string(args.source.splitlines()))
